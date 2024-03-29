from Client.Controllers.BaseController import BaseController

import serial
from serial.tools import list_ports

class Ardunio(BaseController):
    def __init__(self):
        super().__init__()
        self.port = None
        self.baudrate = None
        self.serial = None

    def connect(self, port, baudrate):
        self.port = port # ardunio's serial port (COM for windows, ttyl... for linux, cu.usbmodem... for MacOS)
        self.baudrate = baudrate # baud rate for serial communications
        self.serial = serial.Serial(self.port, self.baudrate) # open up a serial port to communicate with the ardunio

    def action(self, action):
        # check if a serial port is setup for communication
        if self.serial is None:
            raise UserWarning('connect() has not been called.')
        
        # check if action.kick is set...
        if getattr(action, 'kick'):
            print('Kicking...')
            self.serial.write(b'K')

        dribble = getattr(action, 'dribble')

    @staticmethod
    def detect_ardunio_device():
        USBVID = [0x2341, 0x2a03]
        # find all the devices with the specific vendor Ids
        devices = list_ports.comports()
        devices = [x for x in devices if x.vid in USBVID]

        # if no devices are found or more than 1, get confused and return nothing
        if not devices or len(devices) > 1:
            raise UserWarning(f'found {len(devices)} compatible devices; need 1')
        
        # return the port to the ardunio
        return devices[0].device
        
    @staticmethod
    def update(sketch='Kicker'):
        import pyduinocli
        arduino = pyduinocli.Arduino('arduino-cli')
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
        arduino = pyduinocli.Arduino('arduino-cli')
        arduino.compile(fqbn=fqbn, sketch=sketch)
        # upload the ardunio project to detected device
        arduino.upload(fqbn=fqbn, sketch=sketch, port=port)

    @staticmethod
    def add_cls_specific_arguments(parent):
        parser = parent.add_argument_group('ardunio')
        parser.add_argument('--port', type=str, default=None)
        parser.add_argument('--baudrate', type=int, default=19200)
        return parent
