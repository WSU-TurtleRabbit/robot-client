#! /usr/bin/env bash

if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED
curl https://pyenv.run/ | bash

echo 'export PATH=$HOME/.pyenv/bin:$PATH' >> ~./bashrc
echo 'eval "$(pyenv init --path")' >> ~./bashrc 
echo 'eval "$(pyenv virtualenv-init -")' >> ~./bashrc 

exec $SHELL

sudo apt-get install --yes libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libgdbm-dev lzma lzma-dev tcl-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev wget curl make build-essential openssl 
pyenv update

pyenv install 3.7.12
pyenv global 3.7.12

pip install --upgrade pip
sudo pip3 install moteus
pip3 install moteus-pi3hat

sudo apt install python3-pyside2* python3-serial python3-can python3-matplotlib python3-qtconsole
sudo pip3 install asyncqt importlib_metadata pyelftools
sudo pip3 install --no-deps moteus moteus_gui

python3 -m moteus.moteus_tool --pi3hat-cfg '1=1,2=2;3=3,4=4' -t 1,2,3,4

curl https://github.com/mjbots/moteus/releases/download/0.1-20240106/20240106-moteus-1ba9e683e207d792060b45ea435dd6905589a7d4.elf 
for id in $$(seq 1 4);
do 
    python3 -m moteus.moteus_tool --target $id --flash '20240106-moteus-1f4a19554a2b99578cdf566ec5172ee7ddc8304f.elf'   
    python3 -m moteus.moteus_tool --target $id --calibrate  
    
    python3 -m moteus.moteus_tool --target $id --console conf set servopos.position_min nan  
    python3 -m moteus.moteus_tool --target $id --console conf set servopos.position_max nan  
    python3 -m moteus.moteus_tool --target $id --console conf write 
done

pip3 install --editable .