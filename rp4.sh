#! /bin/bash

### This script is for Raspberry Pi on Robot Only . ###

sudo apt-get update
sudo apt-get dist-upgrade --yes

sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED*

libbcm_host='/lib/aarch64-linux-gnu/libbcm_host.so'
[[ -f $libbcm_host.0 ]] && sudo ln -s $libbcm_host.0 $libbcm_host

# upgrade pip 
sudo pip install --upgrade pip

MOTEUS_PATH= "$HOME/moteus-venv"
RC_PATH= "$HOME/robot-client"
VENV_NAME= "venv"
VENV_PATH= "$RC_PATH/$VENV_NAME"

# Step 1: Create the moteus virtual environment if it doesn't exist
if [ ! -d "$MOTEUS_PATH" ]; then
    echo "Installing Moteus Virtual environment and Modules"
    sudo apt-get install --yes python3-pyside2* python3-serial python3-can python3-matplotlib python3-qtconsole
    echo "Creating moteus-venv..."
    python -m venv --system-site-packages moteus-venv
    source $MOTEUS_PATH/bin/activate
else
    echo "moteus-venv already exists. Skipping creation."
    source $MOTEUS_PATH/bin/activate
fi

echo "Checking for Packages for moteus"
pip install moteus
sudo pip3 install asyncqt importlib_metadata pyelftools
sudo pip3 install moteus
sudo pip3 install moteus-pi3hat
sudo pip3 install --no-deps moteus_gui
deactivate

# Step 2: Create your own editable virtual environment
if [ ! -d "$RC_PATH/venv" ]; then
    echo "Creating robot-client venv..."
    python3 -m venv venv
else
    echo "my-venv already exists. Skipping creation."
fi

# Step 3: Find the site-packages directory of moteus-venv
MOTEUS_SITE_PACKAGES=$(python3 -c "import site; print([p for p in site.getsitepackages() if 'moteus-venv' in p][0])")

# Step 4: Add moteus-venv site-packages to PYTHONPATH
echo "Linking moteus-venv to my-venv..."
export PYTHONPATH="$MOTEUS_SITE_PACKAGES:$PYTHONPATH"

# Step 5: Activate my-venv
echo "Activating my-venv..."
source my-venv/bin/activate

# Step 6: Verify that moteus is accessible
python -c "import moteus; print('✅ Moteus is successfully linked!')"

echo "Setup complete. You are now using my-venv with access to moteus!"

# initialising this code module

sudo pip3 install --editable .[prod] # installing Module as editable # add [prod] at the end if you are doing it on RP4

git pull

