#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# convert txt file to fasta file
awk '{print ">"NR"\n"$0}' "$1" > "$1".fasta

# convert fasta file to input file
python "$BASE_PATH"/convertinput.py "$1".fasta "$1".input
rm -f "$1".fasta

# run clustering
source "$BASE_PATH"/venv/bin/activate
python -m clover.main -I "$1".input -O "$2".output -P 0 --no-tag "${@:3}"

# parse clusters
python "$BASE_PATH"/parse_clusters.py "$1".input "$2".output.txt "$2".clusters
rm -f "$1".input
rm -f "$2".output.txt

# convert clusters to consensus sequences
"$BASE_PATH"/../tool_kalign/cluster2consensus.sh "$2".clusters "$2"
rm -f "$2".clusters

exit