import socket
from Client.Shared.Action import Action

class DummyUDPListener:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 50514
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

    def recv(self):
        if self.socket is None:
            raise UserWarning('connect() needs to be called before recv()')
        
        while True:
            message, _ = self.socket.recvfrom(1024)
            action = Action.decode(message)
            print(action)

if __name__ == '__main__':
    recv = DummyUDPListener()
    recv.connect()
    recv.recv()

    