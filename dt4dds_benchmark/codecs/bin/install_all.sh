#!/bin/bash 
set -e

cd "$(dirname "$0")"

printf "\n\nInstalling codec_aeon\n"
printf "=====================\n"
./codec_aeon/install.sh
printf "\n\nFinished installing codec_aeon\n"
printf "=====================\n"

printf "\n\nInstalling codec_fountain\n"
printf "=====================\n"
./codec_fountain/install.sh
printf "\n\nFinished installing codec_fountain\n"
printf "=====================\n"

printf "\n\nInstalling codec_goldman\n"
printf "=====================\n"
./codec_goldman/install.sh
printf "\n\nFinished installing codec_goldman\n"
printf "=====================\n"

printf "\n\nInstalling codec_rs\n"
printf "=====================\n"
./codec_rs/install.sh
printf "\n\nFinished installing codec_rs\n"
printf "=====================\n"

printf "\n\nInstalling codec_hedges\n"
printf "=====================\n"
./codec_hedges/install.sh
printf "\n\nFinished installing codec_hedges\n"
printf "=====================\n"

printf "\n\nInstalling codec_yinyang\n"
printf "=====================\n"
./codec_yinyang/install.sh
printf "\n\nFinished installing codec_yinyang\n"
printf "=====================\n"