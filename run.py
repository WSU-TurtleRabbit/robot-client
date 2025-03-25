#! /usr/bin/python3
from multiprocessing import Process, freeze_support, Manager, Queue

from Client.Dummy.DummyReceiver import DummyReciever
from Client.Dummy.DummyMotor import DummyMotor,DummyMotorControllerFactory

from Client.Coms.Action import Action

from Client.Controllers.Motor3 import MotorController, MotorController3Factory
from Client.Controllers.Arduino import ArduinoController, ArduinoControllerFactory

from Client import SharedResource, SharedResourceProxy


import multiprocessing 
from multiprocessing.managers import BaseManager

import argparse
from functools import reduce
import operator
import logging

class CustomFormatter(logging.Formatter):
    '''logging log object'''

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s: (%(filename)s:%(lineno)d) %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(ch)

import logging
logging.basicConfig(format = "%(asctime)s: (%(filename)s:%(lineno)d) %(levelname)s - %(message)s")
log = logging.getLogger()
log.setLevel(logging.DEBUG)

shared_global_resource = SharedResource()

# global shared reource
def get_shared_global_resource():
    return shared_global_resource

def magic(q: multiprocessing.Queue, shared_global_resource, events: multiprocessing.Event) -> None:
    while True:

        if not q.empty():
            # set the shared namespace variable `action`
            # to the recved action
            action = q.get_nowait()
            # if reduce(operator.or_, (x.is_set() for x in events)):
            #     pass 

            if isinstance(action, Action):
                shared_global_resource.set_action(action)

            elif not isinstance(action,Action) and action is not None:
                raise TypeError(f'action is not type: {Action}, got {type(action)}')
            # set all events and wait...
            # timeout after 1 second if subprocesses freezes
            # for event in events:
            #     event.set()

            # log.info(f'voltage: {shared_global_resource.get_voltage()}')
            # log.info(f'current: {shared_global_resource.get_current()}')
                
if __name__ == '__main__':

    freeze_support()

    no_motor = True
    no_arduino=True
    # # add arguments to run.py
    # parser = argparse.ArgumentParser()
    # parser = MotorController.add_cls_specific_arguments(parser)
    # parser = ArduinoController.add_cls_specific_arguments(parser)
    # args = parser.parse_args()
    # log.debug(f'{args=}')

    # shared queue for inter-process communication
    # max size = 3 
    q = Queue(1)
    # primary UDP communications to TC
    primary = Process(target=DummyReciever(), args=(q,),daemon=True)
    log.info(f"starting {primary=}")
    primary.start() 
    
    # shared inter-process manager
    BaseManager.register("SharedResource", None, SharedResourceProxy)
    BaseManager.register("get_shared_global_resource", get_shared_global_resource)
    m = BaseManager()
    m.start()
    f = m.get_shared_global_resource()
    # events for inter-process messaging
    controller_specific_events = dict()
    controller_specific_events['gc_force_shutdown_event'] = multiprocessing.Event()

    events = []
    processes = [] #list of processes

    # check if the argument --disable-motor-controller is set, if set -> disable motors
    if no_motor is True:
        # log.debug('arg "disable_motor_controller" is true')
        controller_specific_events['tc_action_recv_event'] = multiprocessing.Event() 
        events.append(controller_specific_events['tc_action_recv_event'])
        motor = Process(target=DummyMotorControllerFactory(), args=(f, controller_specific_events,), name="Motor Dummy",daemon=False)
        processes.append(motor)

    elif no_motor is False:
        # log.debug('arg "disable_motor_controller" is false')
        controller_specific_events['tc_action_recv_event'] = multiprocessing.Event() 
        events.append(controller_specific_events['tc_action_recv_event'])
        # initalise motor controller
        motor = Process(target=MotorController3Factory(), args=(f, controller_specific_events,), name="Motor Controller",daemon=False)
        processes.append(motor)


    # check if the argument --disable-arduino-controller is set, if set -> disable arduino
    if no_arduino is False:
        # log.debug('args attr "disable_arduino_controller" is false')
        controller_specific_events['tc_action_recv_event'] = multiprocessing.Event()
        events.append(controller_specific_events['tc_action_recv_event'])
        # initalise arduino controller
        baudrate = 115200
        ardunio = Process(target=ArduinoControllerFactory(), args=(f, controller_specific_events,baudrate, ), name="Ardunio Controller")
        processes.append(ardunio)

    # shared mutliprocessing.Queue for UDP listerner to communicate with distribution()
    secondary = Process(target=magic, args=(q, f, events,), name="Magic", daemon=True)
    log.info(f"starting {secondary=}")
    secondary.start()

    # start all controllers
    for process in processes:
        log.info(f"starting {process=}")
        process.start()

    # wait for sub-processes to end
    secondary.join()
    primary.join()

    for process in processes:
        process.join()
