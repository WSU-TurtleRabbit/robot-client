To add an ssh-key please see the [how-to]() repository

To get started with this python Package (on a raspberry pi 4) do :
```bash
chmod a+x rp4.sh
./rp4.sh
```
The following will be executed:
1. installs the robot client if it is not found at HOME Directory
2. Creates a virtual environment and compiles this Python Project
3. Installs Moteus and dependencies
4. Verifies if this vitual environment has access to Moteus Libraries
5. sets the USB Dialout for Arduino Access via USB.
6. Creates a shortcut to activate the virtual environment (DOES NOT WORK) 

## Usage
To start the client on the robot, we have to first activate the virtual environment in Superuser.
```bash
sudo su
cd $HOME/robot-client
source .venv/bin/activate
```
To allow the robot receive and behave normally, do : 
```bash
./run.py
```
This will then runs the file. if you have any issues, please let one of the team members know. 

To exit : 
```bash
deactivate
exit
```
This shall bring you back to the ordinary user terminal level


To update the ardunio:
```bash 
chmod u+x Arduino/update.py
./Arduino/update.py
```

## Installation - User Computer: 
To set up the development enviroment on User Device(not rp4, but linux), also use
```bash
./rp4.sh
```

If you are not on linux, you will have to self compile this project using the following : 
```bash
python3 -m venv .venv
source .venv/bin/activate # for mac and linux
source .venv/Scripts/activate # for windows

pip install -e . # add user -> pip install --user -e . 

```
Please note that this will not be installing moteus Libraries (our motors and pi3hats depends on this). 
Therefore, anything related to motor will not be execute. 
Best advice : use a Raspberry pi 4 to perform debugging and project development.
Be aware : This project utilises all 4 cores of the RP4, so be aware, and highly recommened to put on a heatsink (a really beefy one that comes with a fan) 

Now you should be good to go ! 
Please let the team know if you have any issues or questions that you'd like to get an answer of ! 
