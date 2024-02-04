#! /usr/bin/python3

from multiprocessing import Process, Queue
import sys
import glob

from Client.Controllers.Motor import Motor
from Client.Controllers.Ardunio import Ardunio

from Client.Receivers.UDP import UDP
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
    listener = UDP()
    robot_action_producer = Process(target=listener.listen_udp, args=(queue,))
    robot_action_producer.start()
    broadcaster = Process(target=listener.listen_broadcast)
    broadcaster.start()

    motor = Motor()

    port = Ardunio.detect_ardunio_device()
    if not kwargs['ardunio-port'] == "":
        port = kwargs['ardunio-port']

    baudrate = kwargs['baud-rate']
    ardunio = Ardunio(port, baudrate)

    pipes = [motor.pipe(), ardunio.pipe()]

    consumer = Process(target=listen, args=(queue, pipes,))
    consumer.start()

    motor_action_listener = Process(target=motor.listen)
    ardunio_action_listener = Process(target=ardunio.listen)

    motor_action_listener.start()
    ardunio_action_listener.start()

    robot_action_producer.join()
    broadcaster.join()
    consumer.join()
    motor_action_listener.join()
    ardunio_action_listener.join()