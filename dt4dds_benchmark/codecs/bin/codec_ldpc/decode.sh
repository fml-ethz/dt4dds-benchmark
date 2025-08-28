#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# run decoding
source "$BASE_PATH"/venv/bin/activate
python "$BASE_PATH"/code/decode.py "$1" "$2" "${@:3}"

exit