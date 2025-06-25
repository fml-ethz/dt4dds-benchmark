#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# run encoding
python2 "$BASE_PATH"/code/encode.py "$@"

exit