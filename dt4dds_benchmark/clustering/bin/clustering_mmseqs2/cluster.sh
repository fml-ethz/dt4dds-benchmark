#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# convert txt file to fasta file
awk '{print ">"NR"\n"$0}' "$1" > "$1".fasta

# run clustering
"$BASE_PATH"/code/build/bin/mmseqs easy-cluster "$1".fasta "$2".output "$1"_tmp "${@:3}"
rm -rf "$1"_tmp
rm -f "$2".output_all_seqs.fasta
rm -f "$2".output_rep_seq.fasta

# parse clusters
python "$BASE_PATH"/parse_clusters.py "$1".fasta "$2".output_cluster.tsv "$2".clusters
rm -f "$1".fasta
rm -f "$2".output_cluster.tsv

# convert clusters to consensus sequences
"$BASE_PATH"/../tool_kalign/cluster2consensus.sh "$2".clusters "$2"
rm -f "$2".clusters

exit