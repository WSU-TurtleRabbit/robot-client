#! /usr/bin/bash

bluetoothctl agent on
bluetoothctl default-agent
bluetoothctl scan on
bluetoothctl pair $xbox_wireless_controller_id
bluetoothctl connect $xbox_wireless_controller_idd