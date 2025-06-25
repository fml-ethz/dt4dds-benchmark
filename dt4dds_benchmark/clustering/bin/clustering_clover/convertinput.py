import sys
import Bio.SeqIO

with open(sys.argv[1], 'r') as fi, open(sys.argv[2], 'w') as fo:
    for i, seq in enumerate(Bio.SeqIO.parse(fi, 'fasta')):
        fo.write(f"{i}, {str(seq.seq)}\n")