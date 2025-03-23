'''controller for arduino (to control kicker and dribbler)'''
from Client.Controllers.BaseController import BaseController
from Client.Coms.Action import Action

import serial
from serial.tools import list_ports
import argparse
import logging

log = logging.getLogger()
log.setLevel(logging.NOTSET)

class ArduinoController(BaseController):
    def __init__(self, shared_global_resource, port: str=None, baudrate: int=None, timeout: int=1) -> None:
        """
            ardunio controller
        attributes:
            port (int): serial COM port
            baudrate (int): baud rate of COM
            timeout (int): time to wait before controller assumes serial.Serial has failed
            serial: (serial.Serial): COM port object
        """
        super().__init__(shared_global_resource)

        self._port: str = port
        self._baudrate: int = baudrate
        self._timeout: int = timeout
        self.serial: serial.Serial = serial.Serial(self._port, self._baudrate, timeout=self._timeout) # open up a serial port to communicate with the ardunio

        log.debug(self)

    def do(self, action: Action) -> None:
        '''
            do() - implements BaseController do(). refer to BaseController do()

        '''
        # check if action.kick is set...
        if action.kick:
            log.info('Kicking...')
            self.serial.write(b'K\n')
        # check if action.dribble is 1 or True, start dribble if so
        if action.dribble == 1:
            log.info('Dribbling...')
            self.serial.write(b'D\n')
         # check if action.dribble is 0 or False, stop dribble if so
        elif action.dribble == 0:
            self.serial.write(b'S\n')

    def read(self) -> str:
        ''''
            read() - read `serial` serial.Serial object

            @return
                str - bytes recieved from `serial`
        '''
        return self.serial.readline()

    def __repr__(self):
        return f'ArdunioController\n\tself.port = {self._port}\n\tself.baudrate = {self._baudrate}\n\tself.timeout = {self._timeout}\n\tself.serial = {self.serial}'
    
    @staticmethod
    def detect_ardunio_device() -> str | None:
        """
            detection of attached ardunio by checking USB device's vendor Id
        @return
            location of attached ardunuio device as a string
        @exception
            RuntimeError if the number of ardunio devices detected is not 1
        """
        USBVID = [0x2341, 0x2a03]
        # find all the devices with the specific vendor Ids
        devices = list_ports.comports()
        devices = [x for x in devices if x.vid in USBVID]

        # if no devices are found or more than 1, get confused and return nothing
        if devices and len(devices) == 1:
            return devices[0].device
        
        # return the port to the ardunio
        raise RuntimeError(f'found {len(devices)} compatible devices; need 1')
        
    @staticmethod
    def update(sketch: str='../../../Arduino/Robot') -> None:
        """
            udpate ardunio's sketch using pyduinocli. requires `pyduinocli`
        @args
            sketch (string): ardunio sketch name i.e., directory containing .ino and .ino name.
        """
        import pyduinocli
        arduino = pyduinocli.Arduino('arduino-cli')
        # list all serial devices
        boards = arduino.board.list()

        port = None
        fqbn = None
        for result in boards['result']['detected_ports']:
            # check if there are any ardunio devices
            log.debug(result)
            if 'matching_boards' in result:
                # get the COM port and FQBN (Fully Qualified Board Name)
                port = result['port']['address']
                fqbn = result['matching_boards'][0]['fqbn']

        # if we don't have the COM port or FQBN, stop
        if port is None or fqbn is None:
            raise RuntimeError('`arduino-cli` found 0 compatible devices')
        # compile the ardunio project
        arduino = pyduinocli.Arduino('arduino-cli')
        arduino.compile(fqbn=fqbn, sketch=sketch)
        # upload the ardunio project to detected device
        arduino.upload(fqbn=fqbn, sketch=sketch, port=port)

    @staticmethod
    def add_cls_specific_arguments(parent: argparse.ArgumentParser) -> None:
        parser = parent.add_argument_group('ArdunioController')
        parser.add_argument('--disable-arduino-controller', action='store_true')
        parent.add_argument('--baud-rate', type=int, default=115200)
        return parent

    def _exit(self):
        '''
        _exit() - implements BaseController _exit()
        '''
        if not self.is_closed:
            self.serial.close()
    
    @property
    def is_closed(self) -> bool:
        '''
        _is_closed() - getter for `serial` (serial.Serial) object's `closed` property 

        @returns
            `serial.Serial` closed property
        '''
        return self.serial.closed
    
    @property
    def port(self):
        return self._port
    
    @property
    def baud_rate(self):
        return self._baudrate
    
class ArduinoControllerFactory():
    @staticmethod
    def __call__(namespace, event, *args) -> None:
        '''
        __call__() constructs an ardunio controller object to listen for action objects

        @args
            namespace : mulitprocessing shared namespace for inter-process communications
            event (mutliprocessing.Event): mulitprocessing shared event for inter-process messaging
        '''
        baudrate = getattr(args, 'baud_rate')
        port = ArduinoController.detect_ardunio_device()
        log.debug(f'detected ardunio on {port}')
        ardunio = ArduinoController(namespace, port, baudrate)
        ardunio.tc_action_recv_event = event['tc_action_recv_event']
        ardunio.gc_force_shutdown_event = event['gc_force_shutdown_event']
        ardunio.run()

if __name__ == '__main__':
    port = ArduinoController.detect_ardunio_device()
    arduino = ArduinoController(port, 115200)
    arduino.update()