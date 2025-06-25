#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code 
rm -rf venv

# get and extract the release
wget https://github.com/TimoLassmann/kalign/archive/refs/tags/v3.4.0.tar.gz
mkdir code
tar -zxvf v3.4.0.tar.gz --strip-components=1 -C code

# create a venv and install the dependencies
python3 -m venv venv
source venv/bin/activate
pip install Biopython

# build the code
cd code
mkdir build 
cd build
cmake ..
make 