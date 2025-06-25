#!/bin/bash 
set -e
BASE_PATH="$(dirname -- "${BASH_SOURCE[0]}")"

# sort and count the sequences
sort "$1" | uniq -c > "$2".sorted
sed -r 's/^\s+//' "$2".sorted | sort -r -n -k1 > "$2".sorted.quantity
rm -f "$2".sorted
cut -f2 -d' ' "$2".sorted.quantity | grep -v 'N' > "$2"
rm -f "$2".sorted.quantity

exit