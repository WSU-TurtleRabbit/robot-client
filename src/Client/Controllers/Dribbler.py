from Client.Controllers.BaseController import BaseController
import serial

class Dribble(BaseController):
    def __init__(self, port, baudrate):
        super().__init__()
        
        self.port = port
        self.baudrate = baudrate
        self.serial = serial.Serial(self.port, self.baudrate)

    def run(self, action):
        super().run(action)
        pass
    
    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent