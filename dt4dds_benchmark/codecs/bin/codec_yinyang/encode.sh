#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# run encoding
source "$BASE_PATH"/venv/bin/activate
python "$BASE_PATH"/caller.py -i "$1" -o "$2" --mode encode "${@:3}"

# save the sequence length for later decoding
awk 'NR==1 {print length; exit}' "$2" > "$4".len

exit