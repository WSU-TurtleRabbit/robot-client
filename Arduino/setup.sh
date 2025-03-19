#! /usr/bin/env bash

# https://arduino.github.io/arduino-cli/0.35/getting-started/

curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

export PATH="$HOME/bin:$PATH"

echo 'export PATH="$HOME/bin:$PATH"'>> ~/.bashrc
source ~/.bashrc

arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr

sudo usermod -a -G dialout $USER #gives user access to serial ports 

pip3 install pyduinocli