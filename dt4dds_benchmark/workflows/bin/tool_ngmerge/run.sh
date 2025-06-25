#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

"$BASE_PATH"/code/NGmerge -1 "$1" -2 "$2" -o "$3" -d -e 20 -z -v

exit