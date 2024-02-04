from Client.Controllers.BaseController import BaseController
import serial
from serial.tools import list_ports

class Ardunio(BaseController):
    def __init__(self, port, baudrate):
        super().__init__()

        self.port = port
        self.baudrate = baudrate
        self.serial = serial.Serial(self.port, self.baudrate)

    def run(self, action):
        super().run(action)
        if getattr(action, 'kick'):
            self.serial.write(b'K')

        dribble = getattr(action, 'dribble')

    @staticmethod
    def detect_ardunio_device():
        USBVID = [0x2341, 0x2a03]
        devices = list_ports.comports()
        devices = [x for x in devices if x.vid in USBVID]

        if not devices or len(devices) > 1:
            return None
        
        return devices[0].device
    
    @staticmethod
    def add_cls_specific_arguments(parent):
        parser = parent.add_argument_group('ardunio')
        parser.add_argument('--ardunio-port', type=str, default=None)
        parser.add_argument('--baud-rate', type=int, defaul=12900)
        return parent