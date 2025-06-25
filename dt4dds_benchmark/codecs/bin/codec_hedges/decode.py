import numpy as np
import NRpyDNAcode as code
import NRpyRS as RS
import sys
import binascii

coderates = np.array([np.NaN, 0.75, 0.6, 0.5, 1./3., 0.25, 1./6.]) # table of coderates 1..6




# 
# USER-SETTABLE PARAMETERS
# 

coderatecode = int(sys.argv[1]) # must be between 1 and 6
strandlen = int(sys.argv[2]) # length of DNA strand without primers
npackets = int(sys.argv[3]) # number of packets to decode
in_filepath = sys.argv[4] # path to file to read DNA from
out_filepath = sys.argv[5] # path to file to decode

# set parameters for DNA constraints (normally not changed, except for no constraint)
max_hpoly_run = 4 # max homopolymer length allowed (0 for no constraint)
GC_window = 12 # window for GC count (0 for no constraint)
max_GC = 8 # max GC allowed in window (0 for no constraint)
min_GC = GC_window - max_GC

# 
# END USER-SETTABLE PARAMETERS
# 



# DO NOT CHANGE
leftprimer = "TCGAAGTCAGCGTGTATTGTATG"
rightprimer = "TAGTGAGTGCGATTAAGCGTGTT" # for direct right appending (no revcomp)
packetIDbytes = 1
seqIDbytes = 1
strandIDbytes = packetIDbytes + seqIDbytes # ID bytes each strand for packet and sequence number
strandrunoutbytes = 2 # confirming bytes end of each strand (see paper)
hlimit = 1000000 # maximum size of decode heap, see paper

# DO NOT CHANGE, HARDCODED INTO C ROUTINES
strandsperpacketcheck = 32  # for RS(255,32)
strandsperpacket = 255  # for RS(255,32)

# compute some derived parameters and set parameters in NRpyDNAcode module
leftlen = len(leftprimer)
rightlen = len(rightprimer)
totstrandlen = strandlen + leftlen + rightlen
strandsperpacketmessage = strandsperpacket - strandsperpacketcheck
(NSALT, MAXSEQ, NSTAK, HLIMIT) = code.getparams() # get settable code parameters
code.setparams(8*strandIDbytes, MAXSEQ, NSTAK, hlimit) # change NSALT and HLIMIT
bytesperstrand = int(strandlen*coderates[coderatecode]/4.)    
messbytesperstrand = bytesperstrand - strandIDbytes - strandrunoutbytes # payload bytes per strand
messbytesperpacket = strandsperpacketmessage * messbytesperstrand # payload bytes per packet of 255 strands
code.setcoderate(coderatecode,leftprimer,rightprimer) # set code rate with left and right primers
code.setdnaconstraints(GC_window, max_GC, min_GC, max_hpoly_run) # set DNA constraints (see paper)


def dnatomess(sequences):

    decoded = set()
    mpackets = [None]*npackets
    epackets = [None]*npackets

    for i in range(npackets):
        mpackets[i] = np.zeros([strandsperpacket, bytesperstrand], dtype=np.uint8)
        epackets[i] = np.ones([strandsperpacket, bytesperstrand], dtype=np.uint8) # everything starts as an erasure
    
    for i in range(len(sequences)):
        (errcode, mess, _, _, _, _) = code.decode(sequences[i], 8*bytesperstrand)

        if errcode > 0:
            # strand is not decodable, trash it
            continue
        if len(mess) < bytesperstrand:
            # message is not completely decoded, trash it
            continue

        # get IDs from message
        #packetID = int("".join([chr(i) for i in mess[0:packetIDbytes]]).encode("hex"), 16)
        packetID = int(binascii.hexlify(mess[0:packetIDbytes]),16)
        seqID = int(binascii.hexlify(''.join([chr(i) for i in mess[packetIDbytes:packetIDbytes+seqIDbytes]])), 16)
        #seqID = int("".join([chr(i) for i in mess[packetIDbytes:packetIDbytes+seqIDbytes]]).encode("hex"), 16)

        if packetID < 0 or packetID >= npackets or seqID < 0 or seqID >= strandsperpacket:
            #print("Bad packetID {} or seqID {}!".format(packetID, seqID))
            # Check if packetID or seqID is out of bounds
            continue


        strandID = (packetID, seqID)

        if strandID in decoded:
            # message is a duplicate, trash it
            continue
        
        # message is good, add it to the packet
        decoded.add(strandID)
        lenmin = min(len(mess), bytesperstrand)
        mpackets[packetID][seqID][:lenmin] = mess[:lenmin]
        epackets[packetID][seqID][:lenmin] = np.zeros(lenmin, dtype=np.uint8)

    return mpackets, epackets




#functions to R-S correct a packet and extract its payload to an array of bytes
def correctmesspacket(packetin, epacket):
    # error correction of the outer RS code from a HEDGES decoded packet and erasure mask
    packet = packetin.copy()
    regin = np.zeros(strandsperpacket,dtype=np.uint8)
    erase = np.zeros(strandsperpacket,dtype=np.uint8)

    for j in range(messbytesperstrand) :
        for i in range(strandsperpacket) :
            regin[i] = packet[i,((j+i)% messbytesperstrand)+strandIDbytes]
            erase[i] = epacket[i,((j+i)% messbytesperstrand)+strandIDbytes]
        locations = np.array(np.argwhere(erase),dtype=np.int32)
        (decoded, _, _, _, _) = RS.rsdecode(regin,locations)
        for i in range(strandsperpacket) :
            packet[i,((j+i)% messbytesperstrand)+strandIDbytes] = decoded[i]
    return packet


def extractplaintext(cpacket) :
    # extract plaintext from a corrected packet
    plaintext = np.zeros(strandsperpacketmessage*messbytesperstrand,dtype=np.uint8)
    for i in range(strandsperpacketmessage) :
        plaintext[i*messbytesperstrand:(i+1)*messbytesperstrand] = (
            cpacket[i,strandIDbytes:strandIDbytes+messbytesperstrand])
    return plaintext



#functions to R-S correct a packet and extract its payload to an array of bytes
def decodemesspackets(all_packets, all_epackets):

    res = []

    for i in range(npackets):
        packet, epacket = all_packets[i], all_epackets[i]
        result = correctmesspacket(packet, epacket)
        decoded_result = extractplaintext(result)
        res.extend(decoded_result)

    return res



nuc2ix = {
    "A": 0,
    "C": 1,
    "G": 2,
    "T": 3
}

# 
# read from file and decode
# 
with open(in_filepath, 'r') as myfile:
    seqs = myfile.read().splitlines()
    seqbits = np.zeros([len(seqs), totstrandlen], dtype=np.uint8)
    for i in range(len(seqs)):
        iseq = leftprimer + seqs[i] + rightprimer
        seqbits[i,:] = [nuc2ix[nuc] for nuc in iseq][0:totstrandlen]

(dpacket, epacket) = dnatomess(seqbits)
data = decodemesspackets(dpacket, epacket)

with open(out_filepath, 'wb') as myfile:
    if data[-1] in (255, 254):
        whitespace = data[-1]
        while data[-1] == whitespace:
            data = data[:-1]
    myfile.write(bytearray([chr(i) for i in data]))