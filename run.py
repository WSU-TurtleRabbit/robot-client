#! /usr/bin/python3
from multiprocessing import Process, Queue, freeze_support, Manager

# from Client.Controllers.Motor import Motor
from Client.Controllers.Ardunio import Ardunio
from Client.Receivers.UDP import UDP
from Client.Shared.Action import Action

import argparse

import socket

def distribution(queue:Queue, namespace, events):
    while True:
        # check if queue has an action
        if not queue.empty():
            action = queue.get()
            # set the shared namespace variable `action`
            # to the recved action
            namespace.action = action
            # set all events and wait...
            # timeout after 1 second if subprocesses freezes
            for event in events:
                event.set(timeout=1)

if __name__ == '__main__':

    freeze_support()

    parser = argparse.ArgumentParser()
    parser = UDP.add_cls_specific_arguments(parser)
    # parser = Motor.add_cls_specific_arguments(parser)
    parser = Ardunio.add_cls_specific_arguments(parser)

    args = parser.parse_args()
    kwargs = vars(args)

    # shared mutliprocessing.Queue for UDP listerner to communicate with distribution()
    queue = Queue()
    communication = UDP()
    primary = Process(target=communication.listen_udp, args=(queue,))
    # start a subprocess for the UDP
    primary.start()
    # secondary = Process(target=communication.listen_broadcast)
    # secondary.start()
    # action = Action(1, 0., 0., 0., 1, 0.)
    # queue.put(action)

    manager = Manager()
    # setup a shared namespace for every subprocess to use
    namespace = manager.Namespace()

    ardunio = Ardunio()
    port = Ardunio.detect_ardunio_device()
    if kwargs['port']:
        port = kwargs['port']
    
    # connect to the port provided at provided baud rate
    ardunio.connect(port, kwargs['baudrate'])

    controllers = [ardunio]

    # get each controller's events
    events = [x.get_event() for x in controllers]

    # distributes the actions recieved from the UDP listener
    distribution = Process(target=distribution, args=(queue, namespace, events))
    distribution.start()

    # start subprocesses thats wait for the controller's events to be set...
    listeners = [Process(target=x.listen, args=(namespace, events)) for x in controllers]
    for listener in listeners:
        listener.start()
   
   # wait for each listener to finish
    for listener in listeners:
        listener.join()

    # wait for the UDP listener to finish
    primary.join()

    # wait for the action distribution to finishs
    distribution.join()