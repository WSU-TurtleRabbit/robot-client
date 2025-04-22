import time
from Client.Coms.Action import Action
from Client.Controllers.Motor import MotorController
import socket
import asyncio
import os 
import moteus
import moteus_pi3hat
import logging 



logging.basicConfig(level=logging.INFO)
log = logging.getLogger("motor_controller")


class AysncMotor(MotorController):
    def __init__(self):
        self.ip = ''
        self.port = 50514
        self.sending_port = 50512
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.buffer = 1024
        self.interval = 0.2
        self._u: float = 1.
        self.sock.setblocking(False)
        self.latest_data = None

        self.servo_bus_map: dict = { 
                    1: [1],
                    2: [2],
                    3: [3],
                    4: [4],
                    5: [32]
                }

        self.transport = moteus_pi3hat.Pi3HatRouter(
                servo_bus_map = self.servo_bus_map
            )
        
        self.controllers: dict = { 
                id: moteus.Controller(id=id, transport=self.transport)
                for id in self.servo_bus_map.keys()
            }
        self.set_direction_of_cw_motion() # sets wheel degrees 
        self.set_wheel_xy_location() # sets distance to centre from each wheel
        self.set_wheel_radius() # sets radius of the wheel
        
        # log.info("motor controller(s) initialised") #END

    async def main(self):
        self.sock.bind((self.ip, self.port))
        # self.sock.listen(1)
        ip = None 
        while ip is None:
            try:
                msg, address = self.sock.recvfrom(self.buffer)
                ip = address[0]
                log.info("connected to ip:{ip}")
                self.sock_sender.bind(('', self.port))
    
            except Exception as e:
                log.error("Error {e} has occured")
                continue


        while True:
            try:
                try:
                    msg, _ = self.sock.recvfrom(self.buffer)
                    self.latest_data = Action.decode(msg)
                except BlockingIOError:
                    if self.latest_data:
                        tel_data = await self.do(self.latest_data)
                        await self._make_stop()
                        voltage = tel_data[0]
                        temp = tel_data[1]

                        data:str = f"Voltage: {voltage} , Temp: {temp}, Command: {self.latest_data}"
                        log.info("Sending data {data}")
                        sender_msg= bytes(str(data).encode())
                        try:
                            self.sock_sender.sendto(sender_msg, (ip[0],self.sending_port))
                            log.info("Data has been sent to %s", ip)
                        except TypeError as e:
                            log.warning("The Code has wrong typing: %s", e)
                            continue

            except KeyboardInterrupt:
                await self._make_stop()
                log.info("Closing program")
                os._exit(130)
                break

            
            
if __name__ == "__main__":
    m = AysncMotor()
    asyncio.run(m.main())




    
