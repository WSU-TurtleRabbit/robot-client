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
chmod u+x setup.sh
sudo ./setup.sh
pip3 install --editable .[prod]
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
