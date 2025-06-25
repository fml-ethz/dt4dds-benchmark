import argparse
import pathlib
import io
import sys
import subprocess
import Bio.SeqRecord, Bio.Seq, Bio.Align, Bio.AlignIO, Bio.motifs, Bio.SeqIO
import time
KALIGN_PATH = str((pathlib.Path(__file__).parent / 'code/build/src/kalign').resolve())
MAX_SEQUENCES = 100

def get_consensus(alignment):
    """ Returns the consensus sequence of a list of sequences. """
    motif = Bio.motifs.create([x.seq for x in alignment], alphabet="ACGT-")
    return motif.consensus


def get_msa(sequences):
    """ Returns a multiple sequence alignment from a list of sequences using kalign. """
    records = [Bio.SeqRecord.SeqRecord(Bio.Seq.Seq(seq), id=str(i)) for i, seq in enumerate(sequences)]
    stdin = io.StringIO()
    Bio.SeqIO.write(records, stdin, "fasta")
    try:
        process = subprocess.run([KALIGN_PATH, "--nthreads", "1", "--type", "dna"], input=stdin.getvalue(), capture_output=True, text=True)
        return Bio.AlignIO.read(io.StringIO(process.stdout), "fasta")
    except Exception as e:
        print(e)
        print(f"Could not cluster sequences [{','.join([str(s) for s in sequences])}], stderr: {process.stderr}, stdin: {process.stdout}")
        raise

def main(args):
    # check for files
    cluster_file = pathlib.Path(args.cluster_file)
    if not cluster_file.exists():
        raise FileNotFoundError(f"Cluster file at {args.cluster_file} does not exist.")
    output_file = pathlib.Path(args.output_file)
    if output_file.exists():
        raise FileExistsError(f"Output file at {args.output_file} already exists.")
    
    # read cluster file, get consensus sequences and write to file
    n_clusters, n_seqs = 0, 0
    with open(cluster_file, 'r') as fi, open(output_file, 'w') as fo:
        for line in fi.readlines():
            n_clusters += 1
            if n_clusters % 1000 == 0:
                print(f"Processed {n_clusters} clusters.", flush=True)
            sequences = [s.strip() for s in line.strip().split(',')]
            n_seqs += len(sequences)
            if len(sequences) > 1:
                aln = get_msa(sequences[:MAX_SEQUENCES])
                consensus = get_consensus(aln).replace('-', '')
            else:
                consensus = sequences[0]
            fo.write(f"{consensus}\n")

    print(f"Done. Wrote {n_clusters} consensus sequences from {n_seqs} individual sequences to {output_file}.")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Get consensus sequences from cluster output.')
    parser.add_argument('cluster_file', type=str, help='Cluster file to process')
    parser.add_argument('output_file', type=str, help='Output file to write')

    args = parser.parse_args()

    try:
        t = time.time()
        main(args)
        print(f"Time elapsed: {time.time() - t:0.2f} seconds.", flush=True)
        sys.exit(0)
    except Exception as e:
        print("Exception occured: ", e, flush=True)
        sys.exit(1)
    
