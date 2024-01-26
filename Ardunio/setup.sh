#! /usr/bin/env bash

# https://arduino.github.io/arduino-cli/0.35/getting-started/

# if [[ "$$" -ne (sh -c 'echo $PPID' && :) ]]; then
#     echo "use '. ./$0'"
#     exit 1
# fi 

curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

echo 'export PATH="$HOME/bin:$PATH"'>> ~/.bashrc
source ~/.bashrc

arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr

sudo usermod -a -G dialout $USER