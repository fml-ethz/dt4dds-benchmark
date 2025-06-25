import sys
import pathlib
import random
import itertools

INPUT_FILE = pathlib.Path(sys.argv[1]).resolve()
OUTPUT_FILE = pathlib.Path(sys.argv[2]).resolve()
SEQ_LENGTH = int(sys.argv[3])


# generate random nucleotides
nucleotides = ['A', 'C', 'G', 'T']
random_nucleotides = itertools.cycle(random.choices(nucleotides, k=100))

# write to file
n_total, n_padded, n_trimmed = 0, 0, 0
with open(INPUT_FILE, "r") as fi, open(OUTPUT_FILE, "w") as fo:
    for line in fi.readlines():
        n_total += 1
        seq = line.strip()
        if len(seq) < SEQ_LENGTH:
            n_padded += 1
            seq += ''.join(next(random_nucleotides) for _ in range(SEQ_LENGTH - len(seq)))
        elif len(seq) > SEQ_LENGTH:
            n_trimmed += 1
            seq = seq[:SEQ_LENGTH]
        fo.write(seq + '\n')

print(f"Total: {n_total}, Padded: {n_padded}, Trimmed: {n_trimmed}")