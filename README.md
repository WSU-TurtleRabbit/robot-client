## Installation
```bash
git clone https://github.com/WSU-TurtleRabbit/robot-client.git 
cd robot-client
```
To set up the development enviroment, use the following commands:
```bash
pip3 install --editable .
```
or to set up the enviroment on a raspberry pi, use the following commands:
```bash
chmod 755 setup.sh
./setup.sh
pip3 install --editable .[prod]
```

## Usage
To start the robot's client, use the following commands:
```bash
chmod 755 run.py
sudo ./run.py
```