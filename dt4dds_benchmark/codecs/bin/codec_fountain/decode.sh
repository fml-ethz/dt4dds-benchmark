#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# padtrim the input file
"$BASE_PATH"/../tool_padtrim/run.sh "$1" "$1".padtrim "$3"

# run decoding
source "$BASE_PATH"/venv/bin/activate
python "$BASE_PATH"/code/decode.py --file_in "$1".padtrim --out "$2" "${@:4}"
rm -f "$1".padtrim

exit