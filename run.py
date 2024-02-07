#! /usr/bin/python3
from multiprocessing import Process, Queue, freeze_support
from multiprocessing.managers import BaseManager

# from Client.Controllers.Motor import Motor
from Client.Controllers.Ardunio import Ardunio
from Client.Receivers.UDP import UDP
# from Client.Shared.Action import Action

import argparse

class ControllerManager(BaseManager):
    pass

def listen(queue:Queue, pipes):
    while True:
        if not queue.empty():
            action = queue.get()
            for pipe in pipes:
                pipe.send(action)

if __name__ == '__main__':

    freeze_support()

    parser = argparse.ArgumentParser()
    parser = UDP.add_cls_specific_arguments(parser)
    # parser = Motor.add_cls_specific_arguments(parser)
    parser = Ardunio.add_cls_specific_arguments(parser)

    args = parser.parse_args()
    kwargs = vars(args)

    queue = Queue()
    communication = UDP()
    robot_udp_listener = Process(target=communication.listen_udp, args=(queue,))
    robot_udp_listener.start()
    robot_broadcast_listener = Process(target=communication.listen_broadcast)
    robot_broadcast_listener.start()
    # action = Action(1, 0., 0., 0., 1, 0.)
    # queue.put(action)

    ControllerManager.register('Ardunio', Ardunio)
    manager = ControllerManager()
    manager.start()

    ardunio = manager.Ardunio()
    port = Ardunio.detect_ardunio_device()
    if kwargs['port']:
        port = kwargs['port']

    ardunio.connect(port, kwargs['baudrate'])
    pipes = [ardunio.pipe()]

    consumer = Process(target=listen, args=(queue, pipes,))
    consumer.start()

    ardunio.listen()


    robot_udp_listener.join()
    robot_broadcast_listener.join()
    consumer.join()