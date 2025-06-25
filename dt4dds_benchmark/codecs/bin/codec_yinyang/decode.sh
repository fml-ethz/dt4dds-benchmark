#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# get the sequence length saved from encoding
LEN=$(cat "$4".len)

# padtrim the input file
"$BASE_PATH"/../tool_padtrim/run.sh "$1" "$1".padtrim "$LEN"

# run decoding
source "$BASE_PATH"/venv/bin/activate
python "$BASE_PATH"/caller.py -i "$1".padtrim -o "$2" --mode decode "${@:3}"
rm -f "$1".padtrim

exit