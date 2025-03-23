#! /usr/bin/python3
from multiprocessing import Process, freeze_support, Manager, Queue

from Client.Dummy.DummyReceiver import DummyReciever
from Client.Coms.Action import Action
from Client.Controllers.Motor2 import MotorController, MotorController2Factory
from Client.Controllers.Arduino import ArduinoController, ArduinoControllerFactory
from Client import SharedResource, SharedResourceProxy
from Client.Dummy.DummyMotor import MotorDummy

from Client.Receivers.RobotUDP import *
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
            action = q.get()
            if reduce(operator.or_, (x.is_set() for x in events)):
                continue 

            if not isinstance(action, Action):
                raise TypeError(f'action is not type: {Action}, got {type(action)}')
            shared_global_resource.set_action(action)
            # set all events and wait...
            # timeout after 1 second if subprocesses freezes
            # for event in events:
            #     event.set()

            # log.info(f'voltage: {shared_global_resource.get_voltage()}')
            # log.info(f'current: {shared_global_resource.get_current()}')

if __name__ == '__main__':

    freeze_support()

    # add arguments to run.py
    parser = argparse.ArgumentParser()
    parser = MotorController.add_cls_specific_arguments(parser)
    parser = ArduinoController.add_cls_specific_arguments(parser)
    args = parser.parse_args()
    log.debug(f'{args=}')

    # shared queue for inter-process communication
    q = Queue()
    # primary UDP communications to TC
    primary = Process(target=DummyReciever(), args=(q,))
    log.info(f"starting {primary=}")
    primary.start() 
    
    # shared inter-process manager
    BaseManager.register("SharedResource", None, SharedResourceProxy)
    BaseManager.register("get_shared_global_resource", get_shared_global_resource)
    m = BaseManager()
    m.start()
    f = m.get_shared_global_resource()
    # events for inter-process mmessaging
    controller_specific_events = dict()
    controller_specific_events['gc_force_shutdown_event'] = multiprocessing.Event()

    events = []
    processes = [] #list of processes

    # check if the argument --disable-motor-controller is set, if set -> disable motors
    if getattr(args,"disable_motor_controller"):
        log.debug('arg "disable_motor_controller" is true')
        events.append(controller_specific_events['tc_action_recv_event'])
        motor = Process(target=MotorDummy(), args=(f, controller_specific_events ,args), name="Motor Dummy")
        processes.append(motor)

    elif not getattr(args, "disable_motor_controller"):
        log.debug('arg "disable_motor_controller" is false')
        controller_specific_events['tc_action_recv_event'] = multiprocessing.Event() 
        events.append(controller_specific_events['tc_action_recv_event'])
        # initalise motor controller
        motor = Process(target=MotorController2Factory(), args=(f, controller_specific_events ,args), name="Motor Controller")
        processes.append(motor)


    # check if the argument --disable-arduino-controller is set, if set -> disable arduino
    if not getattr(args, "disable_arduino_controller"):
        log.debug('args attr "disable_arduino_controller" is false')
        controller_specific_events['tc_action_recv_event'] = multiprocessing.Event()
        events.append(controller_specific_events['tc_action_recv_event'])
        # initalise arduino controller
        ardunio = Process(target=ArduinoControllerFactory(), args=(f, controller_specific_events, args), name="Ardunio Controller")
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
