#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code
rm -rf venv

git clone https://github.com/Scilence2022/DBGPS_Python.git code
python3 -m venv venv
source venv/bin/activate
pip install numpy

cp encode.py code/encode_new.py
cp decode.py code/decode_new.py