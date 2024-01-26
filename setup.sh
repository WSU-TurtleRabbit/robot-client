#! /usr/bin/bash

# if [[ "$$" -ne (sh -c 'echo $PPID' && :) ]]; then
#     echo "use '. ./$0'"
#     exit 1
# fi 

sudo apt-get update
# sudo apt-get upgrade --yes 

[[ ! -d $HOME/.pyenv ]] && curl https://pyenv.run/ | bash

sudo apt-get install --yes libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libgdbm-dev lzma lzma-dev tcl-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev wget curl make build-essential openssl

touch ~/.bashrc

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc 
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc 
# exec $SHELL
source ~/.bashrc

pyenv update
pyenv install 3.7.12
pyenv global 3.7.12

sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED*

libbcm='/lib/aarch64-linux-gnu/libbcm_host.so'
[[ -f $libbcm.0 ]] && sudo mv $libbcm.0 $libbcm

pip install --upgrade pip
sudo pip3 install moteus
pip3 install moteus-pi3hat

sudo apt-get install --yes python3-pyside2* python3-serial python3-can python3-matplotlib python3-qtconsole
sudo pip3 install asyncqt importlib_metadata pyelftools
sudo pip3 install --no-deps moteus_gui