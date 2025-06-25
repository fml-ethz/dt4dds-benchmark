#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code

git clone https://github.com/gui11aume/starcode code
cd code
make