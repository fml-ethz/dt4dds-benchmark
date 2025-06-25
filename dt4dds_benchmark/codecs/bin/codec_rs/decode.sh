#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# padtrim the input file
"$BASE_PATH"/../tool_padtrim/run.sh "$1" "$1".padtrim "$3"

# run decoding
"$BASE_PATH"/code/simulate/texttodna --decode "${@:4}" --input="$1".padtrim --output="$2"
rm -f "$1".padtrim

# if the output is larger than the input, then delete the output file
if [ $(stat -c%s "$2") -gt $(stat -c%s "$1") ]; then
    echo "Output is larger than input, therefore decoding failed. Deleting output file to save space."
    rm -f "$2"
fi

exit