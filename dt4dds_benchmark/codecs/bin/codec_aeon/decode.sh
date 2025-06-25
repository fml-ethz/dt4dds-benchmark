#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# get the sequence length saved from encoding
LEN=$(cat "$2".len)

# padtrim the input file
"$BASE_PATH"/../tool_padtrim/run.sh "$3" "$3".padtrim "$LEN"

# activate virtual environment
source "$BASE_PATH"/venv/bin/activate
cd "$BASE_PATH"/code

trap 'rm -f ./data/"$1"*.*' EXIT

# copy input files to data folder
mv "$2" ./data/"$1".config.json
cp "$2".ini ./data/"$1".ini

# convert input file to fasta
awk '{print ">sequence_" NR "\n" $0}' "$3".padtrim > ./data/"$1".input.fasta
rm -f "$3".padtrim

# run decoding
python ./decode.py -c ./data/"$1".config.json

# copy output files to output folder
cp ./data/results/DEC_"$1".output.zip "$4"

# delete files from data folder
rm -f ./data/"$1"*.*
rm -f ./data/results/DEC_"$1".output.zip

exit