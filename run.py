#! /usr/bin/python3

from multiprocessing import Process, Queue

from Client.Controllers.Motor import Motor
from Client.Controllers.Ardunio import Ardunio
from Client.Receivers.UDP import UDP
# from Client.Shared.Action import Action

import argparse

def listen(queue, pipes):
    while True:
        if not queue.empty():
            action = queue.get()
            for pipe in pipes:
                pipe.send(action)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser = UDP.add_cls_specific_arguments(parser)
    parser = Motor.add_cls_specific_arguments(parser)
    parser = Ardunio.add_cls_specific_arguments(parser)

    args = parser.parse_args()
    kwargs = vars(parser)

    queue = Queue()
    communication = UDP()
    robot_udp_listener = Process(target=communication.listen_udp, args=(queue,))
    robot_udp_listener.start()
    robot_broadcast_listener = Process(target=communication.listen_broadcast)
    robot_broadcast_listener.start()
    # action = Action(1, 0., 0., 0., 1, 0.)
    # queue.put(action)

    motor = Motor()

    port = Ardunio.detect_ardunio_device()
    if not kwargs['port'] is None:
        port = kwargs['port']

    baudrate = kwargs['baudrate']
    ardunio = Ardunio(port, baudrate)

    pipes = [motor.pipe(), ardunio.pipe()]

    consumer = Process(target=listen, args=(queue, pipes,))
    consumer.start()

    actions = [motor.listen, ardunio.listen]
    
    subprocesses = [Process(target=x) for x in actions]
    for subprocess in subprocesses:
        subprocess.start()

    robot_udp_listener.join()
    robot_broadcast_listener.join()
    consumer.join()

    for subprocess in subprocesses:
        subprocess.join()