#! /usr/bin/env -S python3 -B

import pyduinocli
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--arduinocli', '-a', type=str, default='arduino-cli')
    args = parser.parse_args()
    kwargs = vars(args)

    # use ardunio-cli to start pyduinocli
    arduino = pyduinocli.Arduino(kwargs['arduinocli'])

    # list all serial devices
    boards = arduino.board.list()

    port = None
    fqbn = None
    for result in boards['result']:
        # check if there are any ardunio devices
        if 'matching_boards' in result.keys():
            # get the COM port and FQBN (Fully Qualified Board Name)
            port = result['port']['address']
            fqbn = result['matching_boards'][0]['fqbn']

    # if we don't have the COM port or FQBN, stop
    if port is None or fqbn is None:
        raise UserWarning('`arduino-cli` found 0 compatible devices')
    
    # compile the ardunio project
    arduino.compile(fqbn=fqbn, sketch="Kicker")
    # upload the ardunio project to detected device
    arduino.upload(fqbn=fqbn, sketch="Kicker", port=port)