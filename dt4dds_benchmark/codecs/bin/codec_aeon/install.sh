#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code
rm -rf venv

git clone https://github.com/MW55/DNA-Aeon --recurse-submodules code
python3 -m venv venv
source venv/bin/activate
ln -s ../../venv code/NOREC4DNA/venv

cp codebooks.fasta code/codewords/codebooks.fasta
cp codebooks.json code/codewords/codebooks.json
cp encode.py code/encode.py

cd code
pip install -r NOREC_requirements.txt
cmake .
cmake --build .
