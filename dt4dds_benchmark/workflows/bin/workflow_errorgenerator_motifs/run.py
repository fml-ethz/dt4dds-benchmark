import argparse
import pathlib
import numpy as np

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

rng = np.random.default_rng()

parser = argparse.ArgumentParser(description='Error generator to introduce pre-defined error patterns with a bias for motif-containing sequences.')
parser.add_argument('design_file', type=str, help='Design file to simulate')
parser.add_argument('reads_file', type=str, help='Target file for output')
parser.add_argument('--rate_substitutions', type=float, help='Substitution rate', default=0)
parser.add_argument('--rate_deletions', type=float, help='Deletion rate', default=0)
parser.add_argument('--rate_insertions', type=float, help='Insertion rate', default=0)
parser.add_argument('--rate_substitutions_motif', type=float, help='Substitution rate', default=0)
parser.add_argument('--rate_deletions_motif', type=float, help='Deletion rate', default=0)
parser.add_argument('--rate_insertions_motif', type=float, help='Insertion rate', default=0)
parser.add_argument('--coverage', type=float, help='Coverage', default=20)
parser.add_argument('--dropout', type=float, help='Dropout', default=0)
parser.add_argument('--dropout_motif', type=float, help='Dropout', default=0)
args = parser.parse_args()

# get the undesired motifs from the file relative to the script location
script_path = pathlib.Path(__file__).parent.resolve()
motifs = open(f'{script_path}/undesired_sequences.fasta', 'r').read().splitlines()
motifs = set([line.strip() for line in motifs if not line.startswith('>')])

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

            if any(motif in sequence for motif in motifs):
                # introduce errors with motif-specific rates
                dropout = args.dropout_motif
                rate_substitutions = args.rate_substitutions_motif
                rate_deletions = args.rate_deletions_motif
                rate_insertions = args.rate_insertions_motif
            else:
                # introduce errors with general rates
                dropout = args.dropout
                rate_substitutions = args.rate_substitutions
                rate_deletions = args.rate_deletions
                rate_insertions = args.rate_insertions

            if rng.random() > dropout:
                n_added += 1
                for _ in range(int(args.coverage)):
                    read = introduce_substitution(sequence, rate_substitutions)
                    read = introduce_deletion(read, rate_deletions)
                    read = introduce_insertion(read, rate_insertions)
                    f_out.write(read + '\n')
            else:
                n_dropped += 1

tot = n_added + n_dropped
print(f"Added {n_added} ({100*n_added/tot:.1f}%) sequences and dropped {n_dropped} ({100*n_dropped/tot:.1f}%) sequences.")