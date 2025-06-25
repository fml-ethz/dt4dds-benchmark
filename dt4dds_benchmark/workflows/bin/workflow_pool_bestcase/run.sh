#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# run the workflow
python "$BASE_PATH"/run.py "$1" "$(dirname "$2")" "${@:3}"

# merge the paired reads
"$BASE_PATH"/../tool_ngmerge/run.sh "$(dirname "$2")"/R1.fq.gz "$(dirname "$2")"/R2.fq.gz "$2".fq.gz
gunzip "$2".fq.gz

# convert fastq to txt file
awk 'NR%4==2' "$2".fq > "$2"
rm -f "$2".fq

exit