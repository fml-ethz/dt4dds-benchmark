#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# run clustering
python "$BASE_PATH"/clustering.py "$1" "$2".clusters

# convert clusters to consensus sequences
"$BASE_PATH"/../tool_kalign/cluster2consensus.sh "$2".clusters "$2"
rm -f "$2".clusters

exit