#!/bin/bash 
set -e

cd "$(dirname "$0")"

printf "\n\nInstalling clustering_cdhit\n"
printf "=====================\n"
./clustering_cdhit/install.sh
printf "\n\nFinished installing clustering_cdhit\n"
printf "=====================\n"

printf "\n\nInstalling clustering_clover\n"
printf "=====================\n"
./clustering_clover/install.sh
printf "\n\nFinished installing clustering_clover\n"
printf "=====================\n"

printf "\n\nInstalling clustering_mmseqs2\n"
printf "=====================\n"
./clustering_mmseqs2/install.sh
printf "\n\nFinished installing clustering_mmseqs2\n"
printf "=====================\n"

printf "\n\nInstalling clustering_starcode\n"
printf "=====================\n"
./clustering_starcode/install.sh
printf "\n\nFinished installing clustering_starcode\n"
printf "=====================\n"

printf "\n\nInstalling tool_kalign\n"
printf "=====================\n"
./tool_kalign/install.sh
printf "\n\nFinished installing tool_kalign\n"
printf "=====================\n"