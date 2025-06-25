#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code

git clone https://github.com/weizhongli/cdhit.git code
cd code
make