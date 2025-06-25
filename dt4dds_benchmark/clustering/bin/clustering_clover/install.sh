#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code
rm -rf venv

git clone https://github.com/Guanjinqu/Clover.git code
python3 -m venv venv
source venv/bin/activate
cd code
pip install -r requirements.txt
python setup.py install