from Client.Controllers.BaseController import BaseController

class Receiver(BaseController):
    def __init__(self, ip_addr, port):
        super().__init__()

        self.ip_addr = ip_addr
        self.port = port

    @staticmethod
    def add_cls_specific_arguments(parent):
        parser = parent.add_argument_group("UDP")
        parser.add_argument('--ip_addr', type=str)
        parser.add_argument('--port', type=int)
        return parent