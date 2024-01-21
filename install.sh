#! /usr/bin/env bash

sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED
curl https://pyenv.run/ | bash

echo 'export PATH=$HOME/.pyenv/bin:$PATH' >> ~./bashrc
echo 'eval "$(pyenv init --path")' >> ~./bashrc 
echo 'eval "$(pyenv virtualenv-init -")' >> ~./bashrc 
