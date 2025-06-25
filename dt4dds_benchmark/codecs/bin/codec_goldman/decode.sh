#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# padtrim the input file
"$BASE_PATH"/../tool_padtrim/run.sh "$1" "$1".padtrim 117

# run decoding
python2 "$BASE_PATH"/code/decode.py "$1".padtrim "$2" "${@:3}"
rm -f "$1".padtrim

exit