#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# convert txt file to fastq file
awk '{print "@"NR"\n"$0"\n+\n"gensub(/./,"I","g",$0)}' "$1" > "$1".fastq

# run clustering
"$BASE_PATH"/code/starcode -i "$1".fastq -o "$2".starcode --print-clusters "${@:3}"
rm -f "$1".fastq

# convert clusters to consensus sequences
cut -f3 "$2".starcode > "$2".clusters
"$BASE_PATH"/../tool_kalign/cluster2consensus.sh "$2".clusters "$2"
rm -f "$2".starcode
rm -f "$2".clusters

exit