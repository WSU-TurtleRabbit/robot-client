#!/usr/bin/env bash
# Stop execution on any error
set -e

### This script is for Raspberry Pi on Robot Only . ###
### Remember to do chmod 777 ./rp4.sh
# Variables
SHORT_CUT="activate-venv"
VENV_NAME=".venv"
RC_PATH="$HOME/robot-client"
VENV_PATH="$RC_PATH/$VENV_NAME"

check_rp4() {
    if grep -q "Raspberry Pi 4" /proc/device-tree/model; then
        RP4=true
    else
        RP4=false
    fi
}

echo " - - - INITIALISING RP4 - - - " 
echo "Updating and Upgrading System" 
sudo apt-get update
sudo apt-get dist-upgrade --yes

# ---- LEGACY CODE ----
# sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED* # don't need this since working with virtual environments
# libbcm_host='/lib/aarch64-linux-gnu/libbcm_host.so' # can be fixed / replaced by libraspberrypi-dev
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
    echo "$VENV_NAME already exists. reinstalling"
    sudo rm -rf "$VENV_PATH"
    python3 -m venv --system-site-packages "$VENV_NAME"
fi
echo "Activating Virtual Environment $VENV_NAME @ $VENV_PATH . . ."
source $VENV_PATH/bin/activate
source ~/.bashrc

echo "Installing PIP Packages for moteus"
sudo apt install -y \
    python3-pyside2* \
    python3-serial \
    python3-can \
    python3-matplotlib \
    python3-qtconsole \
    build-essential \
    python3-dev


if $RP4; then 
    sudo apt install libraspberrypi-dev # comment when not on raspberry pi 
fi 

pip install asyncqt importlib_metadata pyelftools
pip install --no-deps moteus moteus_gui 
if $RP4; then 
    pip install --no-deps moteus-pi3hat # comment out moteus-pi3hat when not on rp4
    sudo usermod -a -G dialout $USER #for Moteus-pi3hat only
fi
# ---- LEGACY CODE -----
# MOTEUS_SITE_PACKAGES=$(python3 -c "import site; print([p for p in site.getsitepackages() if '.moteus-venv' in p][0])")
# echo "$MOTEUS_SITE_PACKAGES"
# export PYTHONPATH="$MOTEUS_SITE_PACKAGES:$PYTHONPATH"
# ---- LEGACY CODE -----

echo "Verifying possible import moteus in $VENV_PATH"
# Verify that moteus is accessible
python3 -c "import moteus; print('✅ Moteus is successfully linked!')"

echo "Setup complete. You are now using $VENV_PATH with access to moteus!"

# initialising this code package as editable for development
pip install --editable .

## Doing a git pull
git pull


### ADDING DIRECT ACCESS TO ROBOT CLIENT VENV
# Add a Convenient Alias (Optional)
BASHRC_FILE="$HOME/.bashrc"
if ! grep -q "alias $SHORT_CUT=" "$BASHRC_FILE"; then
    echo "Creating ShortCut for accessing This Virtual Environment"

    CMD="source $VENV_PATH/bin/activate"
    echo "alias $SHORT_CUT=\"$CMD\"" >> "$BASHRC_FILE"
    echo "New Command $SHORT_CUT has been added."
    
else 
    echo "Command with $SHORT_CUT Already Exists, try using a different name or remove from $BASHRC_FILE"
fi

# Reload Bash Configuration
echo "Reloading shell configuration..."
source "$BASHRC_FILE"
exec "$SHELL"

echo "You can now type '$SHORT_CUT' in terminal to activate this Virtual Environment"
echo "To Deactivate, type 'deactivate' "
echo "You have reached the end yay !- Emma :D"
