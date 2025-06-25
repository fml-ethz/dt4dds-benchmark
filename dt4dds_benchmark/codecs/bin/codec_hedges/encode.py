import numpy as np
import NRpyDNAcode as code
import NRpyRS as RS
import sys

coderates = np.array([np.NaN, 0.75, 0.6, 0.5, 1./3., 0.25, 1./6.]) # table of coderates 1..6


# 
# USER-SETTABLE PARAMETERS
# 

coderatecode = int(sys.argv[1]) # must be between 1 and 6
strandlen = int(sys.argv[2]) # length of DNA strand without primers
in_filepath = sys.argv[3] # path to file to encode
out_filepath = sys.argv[4] # path to encoded file

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


# 
# OPEN AND READ FILE
# 
with open(in_filepath, 'rb') as myfile: 
    data = myfile.read()
databytes = np.array([c for c in data]).view(np.uint8)
datalen = len(databytes)


# 
# CALCULATE PACKET NUMBER
# 
npackets = int(datalen / messbytesperpacket)
if datalen % messbytesperpacket > 0 : npackets += 1

data_to_send = npackets
print(data_to_send)

print("Encoding %d bytes in %d packets, last packet has %d/%d bytes" % (datalen, npackets, datalen % messbytesperpacket, messbytesperpacket))


# 
# PREPARE PACKET DATA
# 
dataoffset = 0
def getbytes(n): # return next n bytes from data
    global dataoffset
    if dataoffset + n > datalen: 
        whitespace = 255
        last_byte = databytes[-1]
        if last_byte == 255:
            whitespace = 254
        bytes = np.ones(n, dtype=np.uint8) * whitespace
        if dataoffset < datalen:
            bytes[0:datalen-dataoffset] = databytes[dataoffset:datalen]
        dataoffset += n
        return bytes
    else:
        bytes = databytes[dataoffset:dataoffset+n]
        dataoffset += n
        return bytes




# functions to create sequential packets from the plaintext source, and R-S protect them
def createmesspacket(packno):
    
    packet = np.zeros([strandsperpacket,bytesperstrand],dtype=np.uint8)
    
    for i in range(strandsperpacket) :
        packet[i,0:packetIDbytes] = packno
        packet[i,packetIDbytes:packetIDbytes+seqIDbytes] = i
        if i < strandsperpacketmessage :
            ptext = getbytes(messbytesperstrand)
            packet[i,strandIDbytes:strandIDbytes+messbytesperstrand] = ptext

    return packet





def protectmesspacket(packetin) : # fills in the RS check strands
    packet = packetin.copy()
    regin = np.zeros(strandsperpacket,dtype=np.uint8)

    for j in range(messbytesperstrand) :
        for i in range(strandsperpacket) :
            regin[i] = packet[i,((j+i)% messbytesperstrand)+strandIDbytes]
        regout = RS.rsencode(regin)
        for i in range(strandsperpacket) :
            packet[i,((j+i)% messbytesperstrand)+strandIDbytes] = regout[i]
    return packet





# functions to encode a packet to DNA strands, and decode DNA strands to a packet
def messtodna(mpacket) :
    # HEDGES encode a message packet into strands of DNA
    filler = np.array([0,2,1,3,0,3,2,1,2,0,3,1,3,1,2,0,2,3,1,0,3,2,1,0,1,3],dtype=np.uint8)
    dpacket = np.zeros([strandsperpacket,totstrandlen],dtype=np.uint8)

    for i in range(strandsperpacket) :
        dna = code.encode(mpacket[i,:])
        if len(dna) < totstrandlen : # need filler after message and before right primer
            dnaleft = dna[:-rightlen]
            dnaright = dna[-rightlen:]
            dna = np.concatenate((dnaleft,filler[:totstrandlen-len(dna)],dnaright))
            #n.b. this can violate the output constraints (very slightly at end of strand)
        dpacket[i,:len(dna)] = dna
    return dpacket




ix2nuc = {
    0: "A",
    1: "C",
    2: "G",
    3: "T"
}

# 
# encode and write to file
# 
all_dna = []
for ipacket in range(npackets) :
    messpack = createmesspacket(ipacket) # plaintext to message packet
    rspack = protectmesspacket(messpack) # Reed-Solomon protect the packet
    dnapack = messtodna(rspack) # encode to strands of DNA containing payload messplain
    all_dna.extend(dnapack)

with open(out_filepath, 'w') as myfile:
    myfile.write("\n".join(["".join([ix2nuc[i] for i in l[leftlen:-rightlen]]) for l in all_dna]))