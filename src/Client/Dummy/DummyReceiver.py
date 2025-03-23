import socket
from Client.Coms.Action import Action
import argparse
import time
import logging

log = logging.getLogger()
log.setLevel(logging.NOTSET)

class DummyReciever():
    def __init__(self, ip_addr='', port=50514) -> None:
        self.ip_addr = ip_addr
        self.port = port
        self.recv = None # multiprocessing.Queue object

    def __call__(self, queue) -> None:
        recv = DummyReciever()  # make a reciever object
        setattr(recv, 'recv', queue)  # set the attribute recv to hold the multiprocessing Queue to send action objects from UDP to run.py
        recv.connect() # open and bind to the socket
        recv.recieve() # listen to the socket

    def connect(self) -> None:
        # sets up a UDP socket on local machine
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # bind to sock for listening
        self.socket.bind((self.ip_addr, self.port))

    def recieve(self) -> None:
        # check if we are connected
        if self.socket is None:
            raise UserWarning('connect() needs to be called before recv()')
        
        # listen to socket
        while True:
            message, _ = self.socket.recvfrom(1024)
            log.debug(message)
            action = Action.decode(message)
            # send it to another process for distribution to controllers...
            self.recv.put(action, block=True)
            time.sleep(.05)

    @staticmethod
    def add_cls_specific_arguments(parent: argparse.ArgumentParser) -> None:
        return parent