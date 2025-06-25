import argparse
import pathlib
import Bio.SeqIO

parser = argparse.ArgumentParser(description='Parse clusters from MMSeqs2 output.')
parser.add_argument('read_file', type=str, help='Fasta file with reads')
parser.add_argument('cluster_file', type=str, help='Cluster backup file')
parser.add_argument('output_file', type=str, help='Output file to write clusters into')
args = parser.parse_args()

# check for files
read_file = pathlib.Path(args.read_file)
if not read_file.exists():
    raise FileNotFoundError(f"Read file at {args.read_file} does not exist.")
cluster_file = pathlib.Path(args.cluster_file)
if not cluster_file.exists():
    raise FileNotFoundError(f"Cluster file at {args.cluster_file} does not exist.")
output_file = pathlib.Path(args.output_file)
if output_file.exists():
    raise FileExistsError(f"Output file at {args.output_file} already exists.")

# read file with reads, order is the same as in the cluster file
reads = {seq.id: str(seq.seq) for seq in Bio.SeqIO.parse(read_file, 'fasta')}

# read cluster file, get cluster id, then append next read to the corresponding cluster id
clusters = {}
with open(cluster_file, 'r') as f:
    for line in f.readlines():
        cluster_id, seq_id = line.split(sep="\t")
        if cluster_id in clusters:
            clusters[cluster_id.strip()].append(reads[seq_id.strip()])
        else:
            clusters[cluster_id.strip()] = [reads[seq_id.strip()]]

# write clusters to file
with open(output_file, 'w') as f:
    for cluster_id, cluster in clusters.items():
        f.write(f"{','.join(cluster)}\n")