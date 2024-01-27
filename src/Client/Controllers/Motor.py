from Client.Controllers.BaseController import BaseController
import math

import numpy as np
import time

import moteus
import moteus_pi3hat

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

        self.timeout = 0.02
        self.u = 1
    
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


    async def run(self, action):
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
        omega = getattr(action, 'omega')

        cmd = [
            self.servos[id+1].make_position(
                position=math.nan,
                velocity=velocity,
                query=True
            ) for id, velocity in enumerate(self.calculate(vx, vy, omega)) #calculate the velocity and send them back here
            ## *This is a backwards for loop*
        ]
        
        #initialise timer with : 5
        end = time.time() + 5
        # while the time is still in range
        while time.time() < end :
            # loop velocity
            results = await self.transport.cycle(cmd)
            # print debug results
            print(results)
        #stops after the timer has ran out
        await self.transport.cycle(x.make_stop() for x in self.servos.values())


    def calculate(self, omega, vx, vy):
        """_summary_

        Args:
            omega (float): angle velocity (rad/s)
            vx (float): velocity in x direction (cm/s)
            vy (float): velocity in y direction (cm/s)

        Params: 
            vb (matrix (1,3)): compiles the 3 velocity into an array
            H (matrix(4,3)): applies the Omniwheel veloicty matrix
            H.T: transpose H matrix into (3,4)

        Returns:
            w (array): returns all calculated wheel velocity
        """
        vb = np.array([omega, vx, vy])
        vb = np.expand_dims(vb, axis=1)
        H = np.array([[-self.d1, -self.d2, -self.d3, -self.d4],
        [np.cos(self.b1), np.cos(self.b2), -np.cos(self.b3), -np.cos(self.b4)],
        [np.sin(self.b1), -np.sin(self.b2), -np.sin(self.b3), np.sin(self.b4)],
        ])

        w = (H.T@vb)/self.r
        return w
    
    def set_b(self, b1=120, b2=45, b3=-45, b4=-120):
        """_summary_

        Args:
            b1 (int, degrees): wheel degree to centre. Defaults to 120.
            b2 (int, degrees): wheel degree to centre. Defaults to 45.
            b3 (int, degrees): wheel degree to centre. Defaults to -45.
            b4 (int, degrees): wheel degree to centre. Defaults to -120.
            *THESE WILL BE CHANGED INTO RADIANS AFTERWARDS*
        """
        self.b1 = np.radians(b1)
        self.b2 = np.radians(b2)
        self.b3 = np.radians(b3)
        self.b4 = np.radians(b4)

    def set_d(self, d1=(61,35), d2=(50,50), d3=(50,50), d4=(61,32)):
        """_summary_
            Sets the distance of each wheels from the centre using Pythagorus Theorum.

        Args: (mm)
            d1 (tuple, coordinates): . Defaults to (61,35).
            d2 (tuple, coordinates): . Defaults to (50,50).
            d3 (tuple, coordinates): . Defaults to (50,50).
            d4 (tuple, coordinates): . Defaults to (61,32).
            
        """
        self.d1 = np.sqrt((d1[0])^2+(d1[1])^2)/self.u
        self.d2 = np.sqrt(d2[0]^2+d2[1]^2)/self.u
        self.d3 = np.sqrt(d3[0]^2+d3[1]^2)/self.u
        self.d4 = np.sqrt(d4[0]^2+d4[1]^2)/self.u
        print(d1,d2,d3,d4)

    def set_r(self, r=33.5):
        """_summary_
            sets radius of the wheel (applying unit scaling)
        Args:
            r (float, radius(mm)): radius of wheels. Defaults to 33.5.
        """
        self.r = r/self.u

    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent