import argparse
import pathlib
import ast

parser = argparse.ArgumentParser(description='Parse clusters from CD-HIT output.')
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
reads = {}
with open(read_file, 'r') as f:
    for line in f.readlines():
        contents = line.split(sep=",")
        seq_id = contents[0].strip()
        seq = contents[1].strip()
        reads[seq_id] = seq

# read cluster file, get cluster id, then append next read to the corresponding cluster id
clusters = {}
with open(cluster_file, 'r') as f:
    mylist = ast.literal_eval(f.read())
    for seq_id, cluster_id in mylist:
        seq_id = seq_id.split(sep=",")[0].strip()
        cluster_id = cluster_id.split(sep=",")[0].strip()
        if cluster_id not in clusters:
            clusters[cluster_id] = [reads[cluster_id]]
        clusters[cluster_id].append(reads[seq_id])

# write clusters to file
with open(output_file, 'w') as f:
    for cluster_id, cluster in clusters.items():
        f.write(f"{','.join(cluster)}\n")