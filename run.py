#! /usr/bin/python3

from multiprocessing import Process, freeze_support, Manager, Queue
import logging
import argparse
from functools import reduce
import operator
from detect_orange_ball import run_flask_app
from Client.Receivers.Dummy import DummyReciever
from Client.Shared.Action import Action
from Client.Controllers.Motor2 import MotorController, MotorController2Factory
from Client.Controllers.Arduino import ArduinoController, ArduinoControllerFactory
from Client import SharedResource, SharedResourceProxy
from Client.Shared.RobotUDP import *
from multiprocessing.managers import BaseManager
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Logging setup
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

shared_global_resource = SharedResource()

# Global shared resource
def get_shared_global_resource():
    return shared_global_resource

def magic(q: Queue, shared_global_resource, events):
    while True:
        if not q.empty():
            action = q.get()
            if reduce(operator.or_, (x.is_set() for x in events)):
                continue
            if not isinstance(action, Action):
                raise TypeError(f'action is not type: {Action}, got {type(action)}')
            shared_global_resource.set_action(action)

if __name__ == '__main__':
    freeze_support()

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser = MotorController.add_cls_specific_arguments(parser)
    parser = ArduinoController.add_cls_specific_arguments(parser)
    args = parser.parse_args()
    log.debug(f'{args=}')

    # Start Flask app for orange ball detection
    flask_process = Process(target=run_flask_app, name="Flask App", daemon=True)
    log.info(f"Starting {flask_process=}")
    flask_process.start()

    # Shared queue for inter-process communication
    q = Queue()

    # Primary UDP communication
    primary = Process(target=DummyReciever(), args=(q,))
    log.info(f"Starting {primary=}")
    primary.start()

    # Shared resource manager
    BaseManager.register("SharedResource", None, SharedResourceProxy)
    BaseManager.register("get_shared_global_resource", get_shared_global_resource)
    manager = BaseManager()
    manager.start()
    shared_resource = manager.get_shared_global_resource()

    controller_specific_events = {'gc_force_shutdown_event': multiprocessing.Event()}
    events = []
    processes = []

    # Motor controller
    if not getattr(args, "disable_motor_controller"):
        motor = Process(target=MotorController2Factory(), args=(shared_resource, controller_specific_events, args), name="Motor Controller")
        processes.append(motor)

    # Arduino controller
    if not getattr(args, "disable_arduino_controller"):
        arduino = Process(target=ArduinoControllerFactory(), args=(shared_resource, controller_specific_events, args), name="Arduino Controller")
        processes.append(arduino)

    # Start all controllers
    for process in processes:
        log.info(f"Starting {process=}")
        process.start()

    # Wait for processes to end
    primary.join()
    for process in processes:
        process.join()

    # Stop Flask process
    log.info("Terminating Flask process")
    flask_process.terminate()
