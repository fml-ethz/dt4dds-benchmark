#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# add primers back onto sequences
sed 's/^/CCTGCAGAGTAGCATGTC/; s/$/CTGACACTGATGCATCCG/' "$1" > "$1".primers

# convert input to fasta
awk '{print ">Sequence_" NR; print}' "$1".primers > "$1".fasta
rm -f "$1".primers

# run decoding
source "$BASE_PATH"/venv/bin/activate
python "$BASE_PATH"/code/decode_new.py "${@:3}" --input="$1".fasta --output="$2" --type=fasta

rm -f "$1".fasta

exit