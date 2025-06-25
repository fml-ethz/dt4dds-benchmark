#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code

git clone https://github.com/allanino/DNA.git code
cp encode.py code/encode.py
cp decode.py code/decode.py