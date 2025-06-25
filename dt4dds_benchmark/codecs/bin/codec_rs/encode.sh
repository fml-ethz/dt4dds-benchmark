#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# run encoding
"$BASE_PATH"/code/simulate/texttodna --encode "${@:3}" --input="$1" --output="$2"

exit