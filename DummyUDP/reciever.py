#! /usr/bin/env -S python3 -B

import socket
from Client.Shared.Action import Action
from multiprocessing import Queue

class DummyUDPListener:
    def __init__(self):
        self.host = ''
        self.port = 50514
        self.socket = None

    def __call__(self, queue):
        self.connect()
        self.recv(queue)

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))

    def recv(self, queue):
        if self.socket is None:
            raise UserWarning('connect() needs to be called before recv()')
        
        while True:
            message, _ = self.socket.recvfrom(1024)
            action = Action.decode(message)
            queue.put(action)
            print(action)

if __name__ == '__main__':
    queue = Queue()
    recv = DummyUDPListener()
    recv(queue=queue)

    