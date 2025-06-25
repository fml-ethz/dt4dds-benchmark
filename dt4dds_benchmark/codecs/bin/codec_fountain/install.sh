#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code
rm -rf venv

git clone https://github.com/jdbrody/dna-fountain.git code
python3 -m venv venv
source venv/bin/activate
pip install numpy Cython tqdm scipy reedsolo Biopython
cd code
python setup.py build_ext --inplace
python -m pip install -e .