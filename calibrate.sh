#! /usr/bin/bash

# curl -O https://github.com/mjbots/moteus/releases/download/0.1-20240617/20240617-moteus-863c597794066fa77c94828c0d2eb49614d5ebb0.elf
# sudo moteus_tool --pi3hat-cfg "1=2" -t 2 --flash ../20240617-moteus-863c597794066fa77c94828c0d2eb49614d5ebb0.elf
# sudo moteus_tool --pi3hat-cfg '1=1;2=2;3=3;4=4' -t 1,2,3,4 --calibrate
# or 
echo 'calibrating motor 1'
sudo moteus_tool --pi3hat-cfg '1=1;2=2;3=3;4=4' -t 1 calibrate
echo 'calibrating motor 2'
sudo moteus_tool --pi3hat-cfg '1=1;2=2;3=3;4=4' -t 2 calibrate
echo 'calibrating motor 3'
sudo moteus_tool --pi3hat-cfg '1=1;2=2;3=3;4=4' -t 3 calibrate
echo 'calibrating motor 4'
sudo moteus_tool --pi3hat-cfg '1=1;2=2;3=3;4=4' -t 4 calibrate
echo "calibration completed. "

