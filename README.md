## Installation
Add an (SSH key)[https://docs.github.com/en/authentication/connecting-to-github-with-ssh] to your Github account. 
```bash
# key generation
ssh-keygen -t ed25519 -f ~/.ssh/id_github
# registering key on rp4
cat << EOF >  ~/.ssh/config
    HOST github.com-robot-client
    Hostname github.com
    User git
    IdentityFile=/home/pi/.ssh/id_gihub
   
   HOST github.com-shared
    Hostname github.com
    User git
    IdentityFile=/home/pi/.ssh/id_github
EOF
# activating registry
chmod 600 ~/.ssh/config

# user call out to deploy key
cat ~/.ssh/id_github.pub # deploy key will be displayed in terminal.

# now clone the github repositories
git clone git@github.com-robot-client:WSU-TurtleRabbit/robot-client.git 
cd robot-client
```
or to initiate the require modules and environment on a raspberry pi, use the following commands:
```bash
chmod u+x rp4setup.sh
sudo ./rp4setup.sh
```

## Usage
To start the client on the robot, use the following commands:
```bash
chmod u+x run.py
sudo ./run.py
```

To update the ardunio:
```bash 
chmod u+x Arduino/update.py
./Arduino/update.py
```

## Installation - User Computer: 
To set up the development enviroment on User Device, use the following commands:
```bash
./userInstall.sh
```
*If you are on Windows, please create a new terminal in git bash