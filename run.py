#! /usr/bin/python3
from multiprocessing import Process, freeze_support, Manager

# from Client.Controllers.Motor import Motor
from Client.Controllers.Ardunio import Ardunio
from Client.Receivers.UDP import UDP
from Client.Shared.Action import Action

import argparse
import socket

class DummyUDPListener:
    def __init__(self):
        self.host = ''
        self.port = 50514
        self.socket = None
        self.recv = None

    def __call__(self):
        self.connect()
        self.recv(self.pipe)

    def connect(self):
        # sets up a UDP socket on local machine
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # bind to sock for listening
        self.socket.bind((self.host, self.port))

    def recieve(self):
        # check if we are connected
        if self.socket is None:
            raise UserWarning('connect() needs to be called before recv()')
        
        # listen to socket
        while True:
            message, _ = self.socket.recvfrom(1024)
            action = Action.decode(message)
            # send it to another process for distribution to controllers...
            self.recv.send(action)
    
    def pipe(self):
        from multiprocessing import Pipe
        self.recv, _ = Pipe()
        return _

def distribution(connection, namespace, events):
    while True:
        # check if queue has an action

            # set the shared namespace variable `action`
            # to the recved action
            action = connection.recv()
            if not isinstance(action, Action):
                raise TypeError(f'action is not type: {Action}, got {type(action)}')
            namespace.action = action
            # set all events and wait...
            # timeout after 1 second if subprocesses freezes
            for event in events:
                event.set()

if __name__ == '__main__':

    freeze_support()

    parser = argparse.ArgumentParser()
    # parser.add_argument('--develop', type=bool, default=False)
    parser = UDP.add_cls_specific_arguments(parser)
    # parser = Motor.add_cls_specific_arguments(parser)
    parser = Ardunio.add_cls_specific_arguments(parser)

    args = parser.parse_args()
    kwargs = vars(args)

    # shared mutliprocessing.Queue for UDP listerner to communicate with distribution()
    
    # communication = UDP()
    communication = DummyUDPListener()
    pipe = communication.pipe()

    primary = Process(target=communication, args=(pipe,))
    # start a subprocess for the UDP
    primary.start()
    # secondary = Process(target=communication.listen_broadcast)
    # secondary.start()

    manager = Manager()
    # setup a shared namespace for every subprocess to use
    namespace = manager.Namespace()

    ardunio = Ardunio()
    port = Ardunio.detect_ardunio_device_pyserial()
    if kwargs['port']:
        port = kwargs['port']
    
    # connect to the port provided at provided baud rate
    ardunio.connect(port, kwargs['baudrate'])

    controllers = [ardunio]

    # get each controller's events
    events = [x.get_event() for x in controllers]

    # distributes the actions recieved from the UDP listener
    distribution = Process(target=distribution, args=(pipe, namespace, events))
    distribution.start()

    # start subprocesses thats wait for the controller's events to be set...
    listeners = [Process(target=x.listen, args=(namespace,)) for x in controllers]
    for listener in listeners:
        listener.start()
   
   # wait for each listener to finish
    for listener in listeners:
        listener.join()

    # wait for the UDP listener to finish
    primary.join()

    # wait for the action distribution to finishs
    distribution.join()