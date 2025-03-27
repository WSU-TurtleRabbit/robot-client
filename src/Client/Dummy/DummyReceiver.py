import socket
from Client.Coms.Action import Action
import argparse
import time
import logging
from multiprocessing import Queue
from queue import Full # for exception

log = logging.getLogger()
log.setLevel(logging.INFO)

class DummyReciever():
    def __init__(self, ip_addr='', port=50514) -> None:
        self.ip_addr = ip_addr
        self.port = port
        self.recv:Queue = None # multiprocessing.Queue object

    def __call__(self, queue) -> None:
        recv = DummyReciever()  # make a reciever object
        setattr(recv, 'recv', queue)  # set the attribute recv to hold the multiprocessing Queue to send action objects from UDP to run.py
        recv.connect() # open and bind to the socket
        recv.recieve() # listen to the socket
        log.debug("Socket Connection Established")

    def connect(self) -> None:
        timeout = 0.5
        # sets up a UDP socket on local machine
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # bind to sock for listening
        self.socket.bind((self.ip_addr, self.port))
        self.socket.settimeout(timeout)
        log.debug(f"socket {timeout=}")


    def recieve(self) -> None:
        # check if we are connected
        if self.socket is None:
            raise UserWarning('connect() needs to be called before recv()')
        
         # listen to socket
        while True:
            try:
                # try to get a message on socket
                # log.debug("recving now")
                message, _ = self.socket.recvfrom(1024)
                # if there's anything, decode the action -> Action Class
                action = Action.decode(message)
                # log.info(f"RECV : {action=}")
                # put it in queue for other process
                
                self.recv.put_nowait(action) 
            except Full:
                log.error("queue is full, cannot put action")
                # while self.recv.full():
                    # self.recv.get_nowait()
                    
                continue #move on 
            except socket.timeout: # if the recv ran out of time, restart loop. 
                log.debug("recv timeout, restarting")
                continue 
            
                # continue skips this cycle from this point
                # pass re-enter back to the cycle from where it's detected
        

    @staticmethod
    def add_cls_specific_arguments(parent: argparse.ArgumentParser) -> None:
        return parent