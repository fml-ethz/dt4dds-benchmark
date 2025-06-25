#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# run encoding
source "$BASE_PATH"/venv/bin/activate
python "$BASE_PATH"/code/encode.py --file_in "$1" --out "$2" "${@:3}"

exit