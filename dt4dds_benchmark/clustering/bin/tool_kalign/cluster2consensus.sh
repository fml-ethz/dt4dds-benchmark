#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

source "$BASE_PATH"/venv/bin/activate
export PYTHONWARNINGS="ignore"
python "$BASE_PATH"/cluster2consensus.py "$@"

exit