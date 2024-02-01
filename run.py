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

    queue = Queue()
    listener = UDP()
    producer = Process(target=listener.listen, args=(queue,))
    producer.run()

    motor = Motor()

    device = '/dev/cu.usbmodem101' #macOS
    if sys.platform == 'linux':
        device = glob.glob('/etc/ttyACM*')[0] #rpi

    ardunio = Ardunio(device)

    pipes = [motor.pipe(), ardunio.pipe()]

    consumer = Process(target=listen, args=(queue, pipes,))
    consumer.run()

    m_ = Process(target=motor.listen)
    a_ = Process(target=ardunio.listen)

    m_.run()
    a_.run()