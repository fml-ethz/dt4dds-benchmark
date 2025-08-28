#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# padtrim the input file
"$BASE_PATH"/../tool_padtrim/run.sh "$1" "$1".padtrim 112

# run encoding
source "$BASE_PATH"/venv/bin/activate
python "$BASE_PATH"/code/decode.py "$1".padtrim "$2"

rm -f "$1".padtrim
rm -f "$1".padtrim.consensus

exit