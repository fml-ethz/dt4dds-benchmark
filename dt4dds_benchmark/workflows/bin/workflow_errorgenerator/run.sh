#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# run the workflow
python "$BASE_PATH"/run.py "$@"

exit