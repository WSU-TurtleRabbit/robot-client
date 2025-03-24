#! /usr/bin/env python3 -B

import socket
import time
from Client.Coms.Action import Action
import argparse
import logging

log = logging.getLogger()
log.setLevel(logging.NOTSET)
    
class DummyUDPSender:
    ''' send a constant stream of action objects to (ip_addr, port)'''
    def __init__(self, ip_addr: str='127.0.0.1', port: int=50514) -> None:
        self.ip_addr = ip_addr
        self.port = port 
        self.socket = None

    def connect(self) -> None:
        '''
            connect() - creates an UDP socket for `socket`
        '''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self) -> None:
        '''
            send() - sends a packet via `socket` with destintion `ip_addr:port`
        '''
        # check if the attribute `socket` is a socket
        if self.socket is None: 
            raise UserWarning('connect() needs to be called before send_msg()')
        # import math
        while True:
            # vx = math.sin(time.time()) * 100
            # vy = math.cos(time.time()) * 100
            vx = 100
            vy = 0
            msg = Action(robot_id=1, vx=vx, vy=vy, w=0., kick=0, dribble=0).encode()
            print(f'Sending Action... {msg}')
            self.socket.sendto(msg, (self.ip_addr, self.port))
            # time.sleep(0.2) # sleep until the controller has executed the action

    @staticmethod
    def add_cls_specific_arguments(parent: argparse.ArgumentParser) -> argparse.ArgumentParser:
        '''
            add_cls_specific_arguments() - adds the following arguments:
                --ip : destination of `Action` packets
                --port : listening port at destination

            @args
                parent (argparse.ArgumentParser) - argparse (from run.py)

            @returns
                parent (argparse.ArgumentParser) 
        '''
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