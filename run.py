#! /usr/bin/python3

from multiprocessing import Process, Queue

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
    kicker = Ardunio()

    pipes = [motor.pipe(), kicker.pipe()]

    consumer = Process(target=listen, args=(queue, pipes,))
    consumer.run()

    m_ = Process(target=motor.listen)
    k_ = Process(target=kicker.listen)

    m_.run()
    k_.run()