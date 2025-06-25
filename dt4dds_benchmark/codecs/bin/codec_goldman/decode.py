import sys
from dna import dna
import binascii

input_file = sys.argv[1]
output_file = sys.argv[2]
segment_file = sys.argv[3]

# read the number of segments from the segment file
f = open(segment_file, 'r')
n_segments = f.readline().strip()
f.close()
print("Decoding file: " + input_file + " to " + output_file + " with " + n_segments + " segments")

# override the default method for converting the Findex to a file
class DNA(dna.DNA):

    def __Files_to_Findex(self, input_file):
        print("Reading Findex from file: " + input_file)
        Findex = []
        f = open(input_file, 'r')
        for i in f.readlines():
            Findex.append(i.strip())
        f.close()
        return Findex

    def decode_join(self, input_file):
        """ Decode and join DNA zip file into DNA string """
        Findex = self.__Files_to_Findex(input_file)
        Fi = self.__Findex_to_Fi(Findex)
        s5 = self.__Fi_to_S5(Fi)
        s4 = self.__S5_to_S4(s5)
        s0 = self.__S4_to_S0(s4)
        # Save s0 after conversion from hexadecimal to bytes
        f = open(output_file, 'wb')
        f.write(binascii.unhexlify(s0))
        f.close()

    def __Findex_to_Fi(self, Findex):
        # Create inverse table
        dna_inv_table = {
            'A': {'T': '0', 'G': '1', 'C': '2'},
            'C': {'A': '0', 'T': '1', 'G': '2'},
            'G': {'C': '0', 'A': '1', 'T': '2'},
            'T': {'G': '0', 'C': '1', 'A': '2'}
        }
        F = {}
        for Fi in Findex:
            try:
                # Check if reverse complemented
                if Fi[0] != 'T' and Fi[0] != 'A':
                    Fi = self.__reverse_complement(Fi)
                # Remove prepended A/T and appended C/G
                Fi = Fi[1:116] # Prior lenght of Fi is 117
                # Extract ix (last 15) n DNA format
                ix = Fi[-15:]
                Fi = Fi[:-15]
                # Convert ix to trits (IX)
                lastFi = Fi[-1]
                IX = dna_inv_table[ix[0]][lastFi]
                for i in range(1, 15):
                    IX = IX + dna_inv_table[ix[i]][ix[i-1]]
                # Extract ID
                ID = IX[:2]
                # Extract i3 and i
                i3 = IX[2:len(IX)-1]
                i = self.__base3_to_base10(i3)
                # Checksum error
                P = int(IX[-1])
                Pexpected = (int(ID[1-1]) + int(i3[1-1]) + int(i3[3-1]) + 
                            int(i3[5-1]) + int(i3[7-1]) + int(i3[9-1]) + int(i3[11-1])) % 3
                if P != Pexpected:
                    print "Corrupted segment:\nID = %s\ni = %d" %(ID, i)
                    continue
                # Save Fi
                if i not in F:
                    F[i] = []
                if i % 2 == 1:
                    F[i].append(self.__reverse_complement(Fi))
                else:
                    F[i].append(Fi)
            except Exception as e:
                print "Failed segment: " + str(e)
                continue
        return F
    

    def __Fi_to_S5(self, Fi):
        # compile the overlapping segments
        segments = [list() for i in range(max(list(Fi.keys())) + 1 + 3)]
        for i, Fij in Fi.items():
            for f in Fij:
                segments[i].append(f[0:25])
                segments[i+1].append(f[25:50])
                segments[i+2].append(f[50:75])
                segments[i+3].append(f[75:100])

        # join the majority segments
        s5 = ""
        for i in range(len(segments)):
            if i >= int(n_segments) + 3:
                print "Exceeded designated segment count at index " + str(i)
                break
            if len(segments[i]) == 0:
                print "Segments are non-continous at index " + str(i)
            s5 = s5 + self.__majority(segments[i])
        print "Last index: " + str(i)

        return s5
    

    def __majority(self, segments):
        majority = ""
        for i in range(25):
            counts = {'A': 0, 'C': 0, 'G': 0, 'T': 0}
            for segment in segments:
                counts[segment[i]] += 1
            majority += max(counts, key=counts.get)
        return majority


# encode the input file
DNA().decode_join(input_file)
