#!/usr/bin/env bash
# Stop execution on any error
set -e

### This script is for Raspberry Pi on Robot Only . ###
### Remember to do chmod 777 ./rp4.sh
# Variables

VENV_NAME=".venv"
RC_PATH="$HOME/robot-client"
VENV_PATH="$RC_PATH/$VENV_NAME"

echo " - - - INITIALISING RP4 - - - " 
echo "Updating and Upgrading System" 
sudo apt-get update
sudo apt-get dist-upgrade --yes
# ---- LEGACY CODE ----
# sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED* # don't need this since working with virtual environments

# libbcm_host='/lib/aarch64-linux-gnu/libbcm_host.so'
# [[ -f $libbcm_host.0 ]] && sudo ln -s $libbcm_host.0 $libbcm_host
# ---- LEGACY CODE -----
echo "Locating Robot Client Repository"
if [ ! -d "$RC_PATH" ]; then 
    cd $HOME
    echo "Cloning Robot Client"
    git clone "https://github.com/WSU-TurtleRabbit/robot-client.git"
else
    echo "Robot Client found @ $RC_PATH"
fi 
cd $RC_PATH

## if you are using a system that requires python, you will have a message that warns you about externally managed environment
## This means we need to either : break system package (do our modification) or build virtual environments, hence the following
echo "Locating Robot Client Virtual Environment @ $VENV_PATH"
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating robot-client venv..."
    python3 -m venv --system-site-packages "$VENV_NAME"
else
    echo "$VENV_NAME already exists. Skipping creation."
fi
echo "Activating Virtual Environment $VENV_NAME @ $VENV_PATH . . ."
source $VENV_PATH/bin/activate

echo "Installing PIP Packages for moteus"
sudo apt install -y \
    python3-pyside2* \
    python3-serial \
    python3-can \
    python3-matplotlib \
    python3-qtconsole \
    # libraspberrypi-dev # comment when not on raspberry pi 

pip install --upgrade pip
pip install asyncqt importlib_metadata pyelftools
pip install --no-deps moteus moteus_gui #moteus-pi3hat # comment out moteus-pi3hat when not on rp4
sudo usermod -a -G dialout $USER

# ---- LEGACY CODE -----
# MOTEUS_SITE_PACKAGES=$(python3 -c "import site; print([p for p in site.getsitepackages() if '.moteus-venv' in p][0])")
# echo "$MOTEUS_SITE_PACKAGES"
# export PYTHONPATH="$MOTEUS_SITE_PACKAGES:$PYTHONPATH"
# ---- LEGACY CODE -----
echo "Verifying possible import moteus in $VENV_PATH"
# Verify that moteus is accessible
python3 -c "import moteus; print('✅ Moteus is successfully linked!')"

echo "Setup complete. You are now using $VENV_PATH with access to moteus!"

# initialising this code module

pip3 install --editable .

git pull

