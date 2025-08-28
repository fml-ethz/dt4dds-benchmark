#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# run encoding
source "$BASE_PATH"/venv/bin/activate
python "$BASE_PATH"/code/encode_new.py "${@:3}" --input="$1" --output="$2"

# remove the temporary files
rm -f "$2".log
rm -f "$2".tmp

exit