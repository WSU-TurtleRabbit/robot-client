#! /usr/bin/env python3 -B

import socket
import time
from Client.Shared.Action import Action
import argparse

class DummyUDPSender:
    def __init__(self, ip_addr='127.0.0.1', port=50514):
        self.ip_addr = ip_addr
        self.port = port 
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self):
        if self.socket is None:
            raise UserWarning('connect() needs to be called before send_msg()')
        
        while True:
            msg = Action(id=1, vx=0., vy=0., vw=0., kick=1, dribble=0.).encode()
            self.socket.sendto(msg, (self.ip_addr, self.port))
            time.sleep(1.)

    @staticmethod
    def add_cls_specific_arguments(parent):
        parser = parent.add_argument_group('sender')
        parser.add_argument('--ip', type=str, default='127.0.0.1')
        parent.add_argument('--port', type=int, default=50514)
        return parent


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = DummyUDPSender.add_cls_specific_arguments(parser)
    args = parser.parse_args()
    kwargs = vars(args)

    sender = DummyUDPSender(kwargs['ip'], kwargs['port'])
    sender.connect()
    sender.send()