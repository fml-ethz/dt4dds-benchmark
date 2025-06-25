#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code
rm -rf venv

git clone https://github.com/ntpz870817/DNA-storage-YYC.git code
python3 -m venv venv
source venv/bin/activate
python -m pip install numpy
cd code
python -m pip install .