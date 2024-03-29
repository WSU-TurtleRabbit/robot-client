from Client.Controllers.BaseController import BaseController
from Client.Shared.Action import Action
import math

import numpy as np
import time

import moteus
import moteus_pi3hat

import asyncio

class Motor(BaseController):
    def __init__(self):
        """_summary_
            initiate the motor controller with Moteus and Moteus pi3hat
        Params : 
            timeout(float) : standard values for await
            u(int) : unit scaler - used for scaling, input: mm(1) to cm(10) to m (1000)
            servo_bus_map (dict) : maps pi3hat-fdcan id to moteus boards
            transport(pi3hat-router): applys the map onto the pi3hat and initialise
            servos(map) : establish connection of moteus boards and pi3hat
        """

        super().__init__()

        self.interval = 500 # ms
        self.u = 1. # 'mm' * self.u
    
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
                for id in self.servo_bus_map.keys()
            }
        self.set_b() # sets wheel degrees 
        self.set_d() # sets distance to centre from each wheel
        self.set_r() # sets radius of the wheel
        print("Motor Controller initialised") #END


    async def action(self, action):
        """_summary_
            runs the action (moving) applying to wheels

        Args:
            action (Action): from action script import action string (vx,vy,omega)
        Params:
            cmd (dict): complies the motor make position command into a dictionary
            end (timer): sets timer for continuous runtime.
            results(complier) : runs the compiler (cmd) applies to all moteus boards via self.transport
        """

        ### Extracts from the ACTION sent
        vx = getattr(action, 'vx')
        vy = getattr(action, 'vy')
        vw = getattr(action, 'vw')

        print(f"self.calculate({vx}, {vy}, {vw})")

        # if vx, vy and vw are all 0s, stop the motors
        if vx == 0. and vy == 0. and vw == 0.:
            await self.transport.cycle(x.make_stop() for x in self.servos.values())
            return

        cmd = [
            self.servos[id+1].make_position(
                position=math.nan,
                velocity=velocity,
                query=False
            ) for id, velocity in enumerate(self.calculate(vw, vx, vy)) #calculate the velocity and send them back here
            ## *This is a backwards for loop*
        ]

        ts = time.ticks_us()
        while time.ticks_diff(time.ticks_us(), ts) > (self.interval * 1e3):
            # loop velocity
            await self.transport.cycle(cmd)
            # print debug results
            # print(results)
            # pass
        #stops after the timer has ran out
        await self.transport.cycle(x.make_stop() for x in self.servos.values())

    def calculate(self, vw, vx, vy):
        """_summary_
            calculates omniwheels' velocities using args: vx, vy and omega
            applying the omniwheel equation from:
            
            "Modern Robotics: Mechanics, Planning & Control"
            13.2.1

        Args:
            w (float): angle velocity (rad/s)
            vx (float): velocity in x direction (cm/s)
            vy (float): velocity in y direction (cm/s)

        Params: 
            vb (matrix (1,3)): compiles the 3 velocity into an array
            H (matrix(4,3)): applies the Omniwheel veloicty matrix
            H.T: transpose H matrix into (3,4)

        Returns:
            w (array): returns all calculated wheel velocity
        """

        # self.u = 1000
        # self.set_d()
        # self.set_r()

        uv =  np.array([
            (1. / self.r) * ((self.d1 * vw) - (vx * np.sin(self.b1)) + (vy * np.cos(self.b1))),
            (1. / self.r) * ((self.d2 * vw) - (vx * np.sin(self.b2)) + (vy * np.cos(self.b2))),
            (1. / self.r) * ((self.d3 * vw) - (vx * np.sin(self.b3)) + (vy * np.cos(self.b3))),
            (1. / self.r) * ((self.d4 * vw) - (vx * np.sin(self.b4)) + (vy * np.cos(self.b4)))
        ])

        uv = np.multiply(uv, 1/2*np.pi)
        print(f"{__name__}.calculate({vw=}, {vx=}, {vy=}) = {uv=}")
        return uv
        
    def set_b(self, b1=-120, b2=-45, b3=45, b4=120):
        """_summary_

        Args:
            b1 (int, degrees): wheel degree to centre. Defaults to -120.
            b2 (int, degrees): wheel degree to centre. Defaults to -45.
            b3 (int, degrees): wheel degree to centre. Defaults to 45.
            b4 (int, degrees): wheel degree to centre. Defaults to 120.
            *THESE WILL BE CHANGED INTO RADIANS AFTERWARDS*
        """
        self.b1 = np.radians(b1)
        self.b2 = np.radians(b2)
        self.b3 = np.radians(b3)
        self.b4 = np.radians(b4)

        print(f"{self.b1=}, {self.b2=}, {self.b3=}, {self.b4=}")

    def set_d(self, d1=(63.869,36.875), d2=(52.149,-52.149), d3=(-52.149,-52.149), d4=(-63.869,36.875)):
        """_summary_
            Sets the distance of each wheels from the centre using Pythagorus Theorum.

        Args: (mm)
            d1 (tuple, coordinates): . Defaults to (61,35).
            d2 (tuple, coordinates): . Defaults to (50,50).
            d3 (tuple, coordinates): . Defaults to (50,50).
            d4 (tuple, coordinates): . Defaults to (61,32).
            
        """

        self.d1 = np.sqrt(d1[0]**2+d1[1]**2)/self.u
        self.d2 = np.sqrt(d2[0]**2+d2[1]**2)/self.u
        self.d3 = np.sqrt(d3[0]**2+d3[1]**2)/self.u
        self.d4 = np.sqrt(d4[0]**2+d4[1]**2)/self.u

        print(f"{self.d1=}, {self.d2=}, {self.d3=}, {self.d4=}")


    def set_r(self, r=33.5):
        """_summary_
            sets radius of the wheel (applying unit scaling)
        Args:
            r (float, radius): radius of wheels. Defaults to 33.5mm.
        """
        self.r = r/self.u

        print(f"{self.r=}")

    def listen(self, namespace):        
        while True:
            if self.event_action_is_set.is_set():
                action = namespace.action
                self.event_action_is_set.clear()
                asyncio.run(self.run(action))
    
    async def run(self, action):
        if not isinstance(action, Action):
            raise TypeError(f"unexpected type: expected 'Action', got: {action.__class__}")
        await self.action(action)

    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent
