import time
from Client.Coms.Action import Action
from Client.Controllers.Motor import MotorController
from Client.Controllers.Arduino import *
import socket
import asyncio
import os 
import moteus
import moteus_pi3hat
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("motor_controller")


class AysncMotor(MotorController):
    """
    AysncMotor is a subclass of MotorController that asynchronously communicates with 
    motor controllers over UDP and Pi3Hat transport. It handles receiving commands and 
    sending telemetry data like voltage and temperature.
    """

    def __init__(self):
        """
        Initialize networking, transport, and motor controllers.
        """
        self.ip = ''  # IP to bind the UDP server
        self.port = 50514  # Port to receive commands
        self.sending_port = 50512  # Port to send telemetry back
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket for receiving
        self.sock_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket for sending
        self.buffer = 1024  # Buffer size for receiving UDP packets
        self.interval = 0.2  # Interval time (not actively used here)
        self._u: float = 1.  # Control parameter (purpose context-dependent)
        self.sock.setblocking(False)  # Set socket to non-blocking mode
        self.latest_data = None  # Store latest received Action
        self.ArduinoPort = str(ArduinoController.detect_ardunio_device())
        
        self.arduino = ArduinoController(port =self.ArduinoPort, baudrate= 9600)

        # Mapping between bus numbers and servo IDs
        self.servo_bus_map: dict = { 
            1: [1],
            2: [2],
            3: [3],
            4: [4],
            5: [32]
        }

        # Setup transport layer for Moteus motors using Pi3Hat
        self.transport = moteus_pi3hat.Pi3HatRouter(
            servo_bus_map=self.servo_bus_map
        )
        
        # Create controller instances for each servo
        self.controllers: dict = { 
            id: moteus.Controller(id=id, transport=self.transport)
            for id in self.servo_bus_map.keys()
        }

        # Call setup methods (presumably defined in MotorController)
        self.set_direction_of_cw_motion()  # Sets clockwise direction calibration
        self.set_wheel_xy_location()       # Sets wheels' location relative to center
        self.set_wheel_radius()             # Sets radius of each wheel
        
        # log.info("motor controller(s) initialised")  # Log initialization (commented out)

    async def main(self):
        """
        Asynchronous main loop:
        - Waits for an initial client connection.
        - Receives control commands.
        - Executes actions and sends back telemetry data.
        """
        self.sock.bind((self.ip, self.port))  # Bind receiving socket
        
        ip = None 
        while ip is None:
            try:
                msg, address = self.sock.recvfrom(self.buffer)  # Wait for client to send first message
                ip = address[0]
                log.info("connected to ip:{ip}")
                self.sock_sender.bind(('', self.port))  # Bind sender socket after client connects
    
            except Exception as e:
                log.error("Error {e} has occured")  # Log any exception
                await self._make_stop()
                continue

        while True:
            try:
                try:
                    msg, _ = self.sock.recvfrom(self.buffer)  # Try receiving latest message
                    self.latest_data = Action.decode(msg)     # Decode into Action object
                except BlockingIOError:
                    # No new data, use last available command
                    if self.latest_data:
                        tel_data = await self.do(self.latest_data)  # Perform action and get telemetry
                        self.arduino.do(self.latest_data)
                        await self._make_stop()  # Optional stop call
                        voltage = tel_data[0]
                        temp = tel_data[1]

                        # Create telemetry message
                        data: str = f"Voltage: {voltage} , Temp: {temp}, Command: {self.latest_data}"
                        log.info("Sending data {data}")
                        sender_msg = bytes(str(data).encode())
                        try:
                            self.sock_sender.sendto(sender_msg, (ip[0], self.sending_port))  # Send telemetry
                            log.info("Data has been sent to %s", ip)
                        except TypeError as e:
                            log.warning("The Code has wrong typing: %s", e)
                            continue

            except KeyboardInterrupt:
                # Graceful shutdown on Ctrl+C
                await self._make_stop()
                log.info("Closing program")
                os._exit(130)
                break



if __name__ == '__main__':
    a = AysncMotor()
    asyncio.run(a.main())