import time
from Client.Coms.Action import Action
from Client.Controllers.Motor import MotorController
import socket
import yaml 
import asyncio


class AysncMotor(MotorController):
    def __init__(self):
        self.ip = " "
        self.port = 5014
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffer = 1024
        self.interval = 0.05

    async def main(self):
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        msg, ip = self.sock.recvfrom(self.buffer)

        while True:
            msg, ip = self.sock.recvfrom(self.buffer)
            commands = Action.decode(msg)

            while True:
                try:
                    self.sock.recvfrom(self.buffer)
                except self.sock.timeout:
                    break


            tel_data = self.do(commands)
            voltage = tel_data[0]
            temp = tel_data[1]

            data = f"Voltage:{voltage} , Temp:{temp}, Command{commands}"
            data = bytes(data.encode('utf-8'))

            self.sock.sendto(data, (ip, self.buffer))
            
if __name__ == "__main__":
    m = AysncMotor
    asyncio.run(m.main())




    