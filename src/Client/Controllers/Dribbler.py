from Client.Controllers.BaseController import BaseController

class Dribble(BaseController):
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate

    def run(self, action):
        pass
    
    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent