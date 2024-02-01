from Client.Controllers.BaseController import BaseController
import serial

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

        try:
            dribble = getattr(action, 'dribble')
            match dribble:
                case 1:
                    self.serial.write('K1')
                case 2:
                    self.serial.write('K2')
                case 3:
                    self.serial.write('K3')
                case 4:
                    self.serial.write('K4')
        except ValueError:
            pass

    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent