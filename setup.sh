#! /usr/bin/bash

sudo apt-get update
sudo apt-get upgrade --yes

sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED*

libbcm_host='/lib/aarch64-linux-gnu/libbcm_host.so'
[[ -f $libbcm_host.0 ]] && sudo mv $libbcm_host.0 $libbcm_host

pip install --upgrade pip
sudo pip3 install moteus
pip3 install moteus-pi3hat

# sudo apt-get install --yes python3-pyside2* python3-serial python3-can python3-matplotlib python3-qtconsole
# sudo pip3 install asyncqt importlib_metadata pyelftools
# sudo pip3 install --no-deps moteus_gui