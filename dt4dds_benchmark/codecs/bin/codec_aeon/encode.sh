#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# activate virtual environment
source "$BASE_PATH"/venv/bin/activate
cd "$BASE_PATH"/code

trap 'rm -f ./data/"$1"*.*' EXIT

# copy input files to data folder
mv "$2" ./data/"$1".config.json
cp "$3" ./data/"$1".input

# run the codec and transform the fasta output to txt
python encode.py -c ./data/"$1".config.json
grep -v '^>' ./data/"$1".output.fasta > "$4"

# copy ini file to output folder
cp ./data/"$1".ini "$2".ini

# delete files from data folder
rm -f ./data/"$1"*.*

# save the sequence length for later decoding
awk 'NR==1 {print length; exit}' "$4" > "$2".len

exit