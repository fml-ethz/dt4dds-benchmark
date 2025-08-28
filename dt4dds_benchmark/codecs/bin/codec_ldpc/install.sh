#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code
rm -rf venv

git clone --recursive https://github.com/shubhamchandak94/LDPC_DNA_storage.git code
python3 -m venv venv
source venv/bin/activate
pip install numpy

cp encode.py code/encode.py
cp decode.py code/decode.py

cd code
cd LDPC-codes/
make
cd ..

cd kalign2_current/
./configure
make
cd ..

cd python-bchlib/
python setup.py build
python setup.py install
cd ..

wget "https://drive.usercontent.google.com/download?id=16o5Vdzbv7NSpMJFR3PJE4pHtzq2YwpRE&export=download&confirm=t&uuid=96ed412a-93c8-47d9-a290-7397fecd3fc4" -O supp.gen
wget "https://drive.usercontent.google.com/download?id=13h3B1KS8vn8ntFwyja7XwB8HZdzV7Uop&export=download&confirm=t&uuid=25d7d18e-e83e-45e6-a745-de314e53a0eb" -O supp.systematic
wget "https://drive.usercontent.google.com/download?id=14Gz3qzx1yYuzan2zPQHcMo9b1KT223sv&export=download&confirm=t&uuid=d8de867e-9314-4411-be1c-269d2d5e4aaf" -O supp.pchk