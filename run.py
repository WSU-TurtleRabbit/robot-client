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

def detect_ardunio_device():
    '''
    very unreliable ardunio detection function
    it assumes a single serial device is connected at all times...

    needs improvement :D
    '''
    location = None
    if sys.platform == 'linux':
        location = '/dev/ttyACM*'

    if sys.platform == 'darwin':
        location = '/dev/cu.usbmodem*'

    if sys.platform == 'win':
        location = 'COM*'

    try:
        device = glob.glob(location)[0]
    except:
        IndexError("no ardunio device found")
        device = None
    
    return device

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser = UDP.add_cls_specific_arguments(parser)
    parser = Motor.add_cls_specific_arguments(parser)
    parser = Ardunio.add_cls_specific_arguments(parser)

    queue = Queue()
    listener = UDP()
    producer = Process(target=listener.listen, args=(queue,))
    producer.run()

    motor = Motor()

    device = detect_ardunio_device()
    ardunio = Ardunio(device)

    pipes = [motor.pipe(), ardunio.pipe()]

    consumer = Process(target=listen, args=(queue, pipes,))
    consumer.run()

    m_ = Process(target=motor.listen)
    a_ = Process(target=ardunio.listen)

    m_.run()
    a_.run()