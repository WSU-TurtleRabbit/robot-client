#! /usr/bin/python3
from multiprocessing import Process, Queue, freeze_support, Manager

# from Client.Controllers.Motor import Motor
from Client.Controllers.Ardunio import Ardunio
from Client.Receivers.UDP import UDP
# from Client.Shared.Action import Action

import argparse

def distribution(queue:Queue, namespace, events):
    while True:
        if not queue.empty():
            action = queue.get()
            namespace.action = action
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

    queue = Queue()
    communication = UDP()
    primary = Process(target=communication.listen_udp, args=(queue,))
    primary.start()
    # robot_broadcast_listener = Process(target=communication.listen_broadcast)
    # robot_broadcast_listener.start()
    # action = Action(1, 0., 0., 0., 1, 0.)
    # queue.put(action)

    manager = Manager()
    namespace = manager.Namespace()

    ardunio = Ardunio()
    port = Ardunio.detect_ardunio_device()
    if kwargs['port']:
        port = kwargs['port']

    ardunio.connect(port, kwargs['baudrate'])

    controllers = [ardunio]

    events = [x.get_event() for x in controllers]

    distribution = Process(target=distribution, args=(queue, namespace, events))
    distribution.start()

    listeners = [Process(target=x.listen, args=(namespace, events)) for x in controllers]
    for listener in listeners:
        listener.start()
   
    for listener in listeners:
        listener.join()

    primary.join()
    distribution.join()