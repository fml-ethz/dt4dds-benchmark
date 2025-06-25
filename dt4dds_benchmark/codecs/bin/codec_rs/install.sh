#!/bin/bash 
set -e
cd "$(dirname "$0")"

rm -rf code

git clone https://github.com/reinhardh/dna_rs_coding.git code
cd ./code/simulate

# add "#include <bitset>" to the top of the file "../include/GF2M.hpp"
sed -i '1s/^/#include <bitset>\n/' ../include/GF2M.hpp

make texttodna