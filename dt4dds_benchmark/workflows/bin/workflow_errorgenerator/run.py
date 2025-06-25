import argparse
import pathlib
import numpy as np

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

rng = np.random.default_rng()

parser = argparse.ArgumentParser(description='Error generator to introduce pre-defined error patterns.')
parser.add_argument('design_file', type=str, help='Design file to simulate')
parser.add_argument('reads_file', type=str, help='Target file for output')
parser.add_argument('--rate_substitutions', type=float, help='Substitution rate', default=0)
parser.add_argument('--rate_deletions', type=float, help='Deletion rate', default=0)
parser.add_argument('--rate_insertions', type=float, help='Insertion rate', default=0)
parser.add_argument('--coverage', type=float, help='Coverage', default=20)
parser.add_argument('--dropout', type=float, help='Dropout', default=0)
args = parser.parse_args()

design_file = pathlib.Path(args.design_file)
if not design_file.exists():
    raise FileNotFoundError(f"Design file at {args.design_file} does not exist.")

reads_file = pathlib.Path(args.reads_file)
if reads_file.exists():
    raise FileExistsError(f"Reads file at {args.reads_file} already exists.")


def introduce_substitution(sequence: str, rate: float):
    new_bases = []
    for base in sequence:
        if rng.random() < rate:
            new_bases.append(rng.choice([b for b in ['A', 'C', 'G', 'T'] if b != base]))
        else:
            new_bases.append(base)
    return ''.join(new_bases)


def introduce_deletion(sequence: str, rate: float):
    return ''.join([base for base in sequence if rng.random() > rate])


def introduce_insertion(sequence: str, rate: float):
    new_bases = []
    for base in sequence:
        new_bases.append(base)
        if rng.random() < rate:
            new_bases.append(rng.choice(['A', 'C', 'G', 'T']))
    return ''.join(new_bases)

n_dropped, n_added = 0, 0
with open(design_file, 'r') as f_in, open(reads_file, 'w') as f_out:
    for line in f_in:
        if line.startswith('>'):
            continue
        else:
            sequence = line.strip()
            if rng.random() > args.dropout:
                n_added += 1
                for _ in range(int(args.coverage)):
                    read = introduce_substitution(sequence, args.rate_substitutions)
                    read = introduce_deletion(read, args.rate_deletions)
                    read = introduce_insertion(read, args.rate_insertions)
                    f_out.write(read + '\n')
            else:
                n_dropped += 1

tot = n_added + n_dropped
print(f"Added {n_added} ({100*n_added/tot:.1f}%) sequences and dropped {n_dropped} ({100*n_dropped/tot:.1f}%) sequences.")