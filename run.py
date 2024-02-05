#! /usr/bin/python3

from multiprocessing import Process, Queue

from Client.Controllers.Motor import Motor
from Client.Controllers.Ardunio import Ardunio
from Client.Receivers.UDP import UDP
from Client.Shared.State import State

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
    robot_action_producer = Process(target=communication.listen_udp, args=(queue,))
    robot_action_producer.start()
    robot_broadcast_listener = Process(target=communication.listen_broadcast)
    robot_broadcast_listener.start()

    motor = Motor()

    port = Ardunio.detect_ardunio_device()
    if not kwargs['ardunio-port'] is None:
        port = kwargs['ardunio-port']

    baudrate = kwargs['baud-rate']
    ardunio = Ardunio(port, baudrate)

    pipes = [motor.pipe(), ardunio.pipe()]

    consumer = Process(target=listen, args=(queue, pipes,))
    consumer.start()

    actions = [motor.listen, ardunio.listen]
    
    subprocesses = [Process(target=x) for x in actions]
    for subprocess in subprocesses:
        subprocess.start()

    robot_action_producer.join()