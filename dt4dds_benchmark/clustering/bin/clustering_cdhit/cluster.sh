#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# convert txt file to fasta file
awk '{print ">"NR"\n"$0}' "$1" > "$1".fasta

# run clustering
"$BASE_PATH"/code/cd-hit-est -i "$1".fasta -o "$2".fasta -sf 1 -bak 1  "${@:3}"

# parse clusters
python "$BASE_PATH"/parse_clusters.py "$1".fasta "$2".fasta.bak.clstr "$2".clusters
rm -f "$1".fasta
rm -f "$2".fasta
rm -f "$2".fasta.clstr
rm -f "$2".fasta.bak.clstr

# convert clusters to consensus sequences
"$BASE_PATH"/../tool_kalign/cluster2consensus.sh "$2".clusters "$2"
rm -f "$2".clusters

exit