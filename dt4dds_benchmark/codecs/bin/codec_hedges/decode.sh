#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# padtrim the input file
"$BASE_PATH"/../tool_padtrim/run.sh "$4" "$4".padtrim "$2"

# run decoding
python2 "$BASE_PATH"/code/decode.py "$1" "$2" "$3" "$4".padtrim "$5"
rm -f "$4".padtrim

exit