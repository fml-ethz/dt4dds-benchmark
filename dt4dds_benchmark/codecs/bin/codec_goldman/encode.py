import sys
from dna import dna

input_file = sys.argv[1]
output_file = sys.argv[2]
segment_file = sys.argv[3]
print("Encoding file: " + input_file + " to " + output_file)

# override the default method for converting the Findex to a file
class DNA(dna.DNA):

    def __Findex_to_Files(self, Findex, input_file):
        print("Writing Findex to file: " + output_file)
        f = open(output_file, 'w')
        for i in Findex:
            f.write(i)
            f.write('\n')
        f.close()
        print("Used " + str(len(Findex)) + " indexes")

        # save segment count
        fi = open(segment_file, 'w')
        fi.write(str(len(Findex)))
        fi.close()

# encode the input file
DNA().encode_split(input_file)
