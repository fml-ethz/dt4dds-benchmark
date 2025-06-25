#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

python "$BASE_PATH"/padtrim.py "$@"
exit