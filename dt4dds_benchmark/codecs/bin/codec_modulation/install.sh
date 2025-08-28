#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code
rm -rf venv

git clone https://github.com/BertZan/Modulation-based-DNA-storage.git code
python3 -m venv venv
source venv/bin/activate
pip install numpy

cp encode.py code/encode.py
cp decode.py code/decode.py