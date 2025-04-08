#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

### This script is for Raspberry Pi 4 on Robot Only ###
### chmod +x ./rp4.sh before running ###

# Variables
SHORT_CUT="activate-venv"
VENV_NAME=".venv"
RC_REPO="https://github.com/WSU-TurtleRabbit/robot-client.git"
RC_PATH="$HOME/robot-client"
VENV_PATH="$RC_PATH/$VENV_NAME"
BASHRC_FILE="$HOME/.bashrc"

# Functions
check_rp4() {
    grep -q "Raspberry Pi 4" /proc/device-tree/model 2>/dev/null
}

echo " - - - INITIALISING RP4 - - - "

echo "🔧 Updating and Upgrading System"
sudo apt-get update
sudo apt-get dist-upgrade -y

# Check if directory exists and clone if missing
if [ ! -d "$RC_PATH" ]; then 
    echo "📦 Cloning Robot Client repository..."
    git clone "$RC_REPO" "$RC_PATH"
else
    echo "✅ Robot Client found at $RC_PATH"
fi 

cd "$RC_PATH"

# Create virtual environment if not exists
if [ ! -d "$VENV_PATH" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv --system-site-packages "$VENV_NAME"
else
    echo "✅ Virtual environment already exists."
fi

echo "⚡ Activating virtual environment..."
source "$VENV_PATH/bin/activate"

# Install system dependencies
echo "📦 Installing required apt packages..."
sudo apt install -y \
    python3-pyside2.* \
    python3-serial \
    python3-can \
    python3-matplotlib \
    python3-qtconsole

if check_rp4; then
    echo "📦 Installing Pi-specific package: libraspberrypi-dev"
    sudo apt install -y libraspberrypi-dev
fi

# Install Python packages
echo "📦 Installing Python packages via pip..."
pip install --upgrade pip
pip install asyncqt importlib_metadata pyelftools
pip install --no-deps moteus moteus_gui

if check_rp4; then
    pip install --no-deps moteus-pi3hat
    sudo usermod -a -G dialout "$USER"
fi

# Verify moteus import
echo "🔍 Verifying moteus installation..."
python -c "import moteus; print('✅ Moteus is successfully linked!')"

# Editable install
echo "🔧 Installing robot client in editable mode..."
pip install --editable .

# Update repo
echo "🔄 Pulling latest changes from Git..."
git pull

# Add alias to bashrc
if ! grep -q "alias $SHORT_CUT=" "$BASHRC_FILE"; then
    echo "🔗 Adding alias '$SHORT_CUT' to $BASHRC_FILE"
    echo "alias $SHORT_CUT='source $VENV_PATH/bin/activate'" >> "$BASHRC_FILE"
else
    echo "⚠️ Alias '$SHORT_CUT' already exists in $BASHRC_FILE"
fi

# Source bashrc and reload shell
echo "🔁 Reloading shell configuration..."
source "$BASHRC_FILE"
exec "$SHELL"

echo "🎉 Setup complete! Type '$SHORT_CUT' to activate the virtual environment."
echo "To deactivate, type 'deactivate'."
echo "You have reached the end — yay! 😄 - Emma"