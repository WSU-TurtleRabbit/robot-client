#! /bin/bash

### This script is for Raspberry Pi on Robot Only . ###


# Exit immediately if a command exits with a non-zero status
set -e

sudo apt-get update
sudo apt-get dist-upgrade --yes
sudo apt install -y python3 python3-pip python3-venv python3-serial git
sudo pip install --upgrade pip

# remove blockage
# sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED*

#setup coms
libbcm_host='/lib/aarch64-linux-gnu/libbcm_host.so'
[[ -f $libbcm_host.0 ]] && sudo ln -s $libbcm_host.0 $libbcm_host

#setup usb access
sudo usermod -a -G dialout $USER

#path variables, do not change
RC="rc"
MOTEUS_VENV="moteus-venv"
RC_VENV="$RC-venv"
RC_PATH="$HOME/robot-client"
MOTEUS_PATH="$HOME/$MOTEUS_VENV"
RC_VENV_DIR="$RC_PATH/$RC_VENV"

# Create the moteus virtual environment if it doesn't exist
if [ ! -d "$MOTEUS_PATH" ]; then
    echo "Installing Moteus Virtual environment and Dependencies"
    sudo apt-get install --yes python3-pyside2* python3-serial python3-can python3-matplotlib python3-qtconsole
    echo "Creating $MOTEUS_VENV @ $MOTEUS_PATH"
    python -m venv --system-site-packages "$MOTEUS_VENV"
    source "$MOTEUS_PATH/bin/activate" || { echo "cannot activate moteus venv"; exit 1; }
else
    echo "$MOTEUS_VENV already exists @$MOTEUS_PATH Skipping creation."
    source $MOTEUS_PATH/bin/activate || {echo "cannot activate moteus venv"; exit 1;}
fi

echo "Checking for Packages for moteus"
sudo pip3 install moteus
sudo pip3 install asyncqt importlib_metadata pyelftools
sudo pip3 install moteus
sudo pip3 install moteus-pi3hat
sudo pip3 install --no-deps moteus_gui
deactivate

echo "Checking for Robot Client Module"
if [ ! -d "$RC_PATH" ]; then
    echo "cloning Robot Client Module from git hub"
    git clone https://github.com/WSU-TurtleRabbit/robot-client
    else 
        echo "Robot Client is found"
fi
cd $RC_PATH

# Step 2: Create your own editable virtual environment
if [ ! -d "$RC_VENV_DIR" ]; then
    echo "Creating robot-client venv..."
    python3 -m venv $RC_VENV

else
    echo "venv @$RC_VENV already exists. Skipping creation."
fi

curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

export PATH="$HOME/bin:$PATH"

echo 'export PATH="$HOME/bin:$PATH"'>> ~/.bashrc
source ~/.bashrc

arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr

pip3 install pyduinocli

# Find the site-packages directory of moteus-venv
MOTEUS_SITE_PACKAGES=$(python3 -c "import site; paths = [p for p in site.getsitepackages() if '$MOTEUS_VENV' in p]; print(paths[0] if paths else '')")

# Add moteus-venv site-packages to PYTHONPATH
echo "Linking $MOTEUS_VENV to $RC_VENV..."
export PYTHONPATH="$MOTEUS_SITE_PACKAGES:$PYTHONPATH"

# Step 5: Activate my-venv
echo "Activating $RC_VENV..."
source $RC_VENV/bin/activate

# Verify that moteus is accessible
python -c "import moteus; print('✅ Moteus is successfully linked!')"

echo "Setup complete. venv now with access to moteus!"

# initialising this code module

pip3 install --editable .[prod] # installing Module as editable # add [prod] at the end if you are doing it on RP4

git pull

### ADDING DIRECT ACCESS TO ROBOT CLIENT VENV
# Add a Convenient Alias (Optional)
BASHRC_FILE="$HOME/.bashrc"
if ! grep -q "alias $RC=" "$BASHRC_FILE"; then
    CMD="source $RC_VENV_DIR/bin/activate"
    echo "alias $RC=\"$CMD\"" >> "$BASHRC_FILE"
fi

# Reload Bash Configuration
echo "Reloading shell configuration..."
source "$BASHRC_FILE"


# ✅ Setup Complete
echo "Setup Complete! Please reboot your Raspberry Pi to apply changes."
echo "After reboot, type '$RC' to activate your virtual environment."
