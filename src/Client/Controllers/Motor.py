from Client.Controllers.BaseController import BaseController
import math

import numpy as np

import moteus
import moteus_pi3hat

class Motor(BaseController):
    async def __init__(self, timeout=.02):
        super().__init__()

        self.timeout = timeout
        self.servo_bus_map = {
                1: [1],
                2: [2],
                3: [3],
                4: [4]
            }

        self.transport = moteus_pi3hat.Pi3HatRouter(
            servo_bus_map = self.servo_bus_map
        )

        self.servos = { 
            id: moteus.Controller(id=id, transport=self.transport)
            for id in self.servo_bus_map.values
        }

        await self.transport.cycle(x.make_stop() for x in self.servos.values())

        self.set_b()
        self.set_d()
        self.set_r()


    async def run(self, action):
        vx = getattr(action, 'vx')
        vy = getattr(action, 'vy')
        omega = getattr(action, 'omega')

        velocities = self.convert(vx, vy, omega)

        cmd = [
            self.servos[id+1].make_position(
                position=math.nan,
                velocity=velocity,
                query=True
            ) for id, velocity in enumerate(velocities)
        ]

        results = await self.transport.cycle(cmd)

    def convert(self, omega, vx, vy):
        vb = np.array(*locals().values())
        H = np.array([[-self.d1, -self.d2, -self.d3, -self.d4],
        [np.cos(self.b1), np.cos(self.b2), -np.cos(self.b3), -np.cos(self.b4)],
        [np.sin(self.b1), -np.sin(self.b2), -np.sin(self.b3), np.sin(self.b4)],
        ])

        u = (H.T@vb)/self.r
        return u
    
    def set_b(self, b1=120, b2=45, b3=-45, b4=-120):
        self.b1 = np.radians(b1)
        self.b2 = np.radians(b2)
        self.b3 = np.radians(b3)
        self.b4 = np.radians(b4)

    def set_d(self, d1=(61,35), d2=(50,-50), d3=(-50,-50), d4=(-61,32)):
        self.d1 = np.sqrt(d1[0]^2+d1[1]^2)
        self.d2 = np.sqrt(d2[0]^2+d2[1]^2)
        self.d3 = np.sqrt(d3[0]^2+d3[1]^2)
        self.d4 = np.sqrt(d4[0]^2+d4[1]^2)

    def set_r(self, r=33.5):
        self.r = r

    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent



    