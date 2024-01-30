#! /usr/bin/python3

from multiprocessing import Process, Queue

from Client.Controllers.Motor import Motor
from Client.Controllers.Kicker import Kicker

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
    producer.start()

    motor = Motor()
    # kicker = Kicker()

    pipes = [motor.pipe()]

    consumer = Process(target=listen, args=(queue, pipes,))
    consumer.start()

    motor_ = Process(target=motor.listen)
    # kicker_ = kicker.listen()

    motor_.start()
    # kicker_.start()

    producer.join()
    consumer.join()

    motor_.join()
    # kicker_.join()

    
