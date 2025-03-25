'''controller for moteus motor controllers'''
from Client.Controllers.BaseController import BaseController
from Client.Coms.Action import Action
import math

import numpy as np
import time

import logging

log = logging.getLogger()
log.setLevel(logging.NOTSET)

try:
    import moteus
except ImportError as e:
    log.warning(e)
try: 
    import moteus_pi3hat # This requires pi3hat on top of RP4
except ImportError as e:
    log.warning(e)

import asyncio
import argparse

class MotorController(BaseController):
    # VELOCITY_LOWER_LIMIT: float = .001 # rate of .1 revolutions per second
    VELOCITY_UPPER_LIMIT: float = 100.

    # (x, y) coordinates from robot's centre to wheel's centre in mm
    OMNIWHEEL_1_XY_COORDINATES: tuple[float, float] = (63.869,36.875)
    OMNIWHEEL_2_XY_COORDINATES: tuple[float, float] = (52.149,-52.149)
    OMNIWHEEL_3_XY_COORDINATES: tuple[float, float] = (-52.149,-52.149)
    OMNIWHEEL_4_XY_COORDINATES: tuple[float, float] = (-63.869,36.875)

    # angle of wheel's direction of travel when rotating clockwise
    # referenced from the robot's forward movement
    OMNIWHEEL_1_CW_ANGLE_DEG: int = -120
    OMNIWHEEL_2_CW_ANGLE_DEG: int = -45
    OMNIWHEEL_3_CW_ANGLE_DEG: int = 45
    OMNIWHEEL_4_CW_ANGLE_DEG: int = 120

    # radius of omniwheel in mm
    OMNIWHEEL_1_RADIUS: float = 33.5
    OMNIWHEEL_2_RADIUS: float = 33.5
    OMNIWHEEL_3_RADIUS: float = 33.5
    OMNIWHEEL_4_RADIUS: float = 33.5

    def __init__(self, shared_global_resource) -> None:
        """_summary_
            initiate the motor controller with Moteus and Moteus pi3hat
        Params : 
            timeout(float) : standard values for await
            u(int) : unit scaler - used for scaling, input: mm(1) to cm(10) to m (1000)
            servo_bus_map (dict) : maps pi3hat-fdcan id to moteus boards
            transport(pi3hat-router): applys the map onto the pi3hat and initialise
            servos(map) : establish connection of moteus boards and pi3hat
        """

        super().__init__(shared_global_resource)

        self._interval: float = 1 # ms
        self._u: float = 1. # motor movement is in 'mm' can be scaled by changing self.u
        self.vx: float = 0.
        self.vy: float = 0.
        self.vw: float = 0.
        self._action_interval = 0.5# second
        self._last_action_time: float = 0
        
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

        self.diagnostics = moteus.Controller(id=32, transport=self.transport)
        self.steam = moteus.Stream(self.diagnostics)
        
        self.set_direction_of_cw_motion() # sets wheel degrees 
        self.set_wheel_xy_location() # sets distance to centre from each wheel
        self.set_wheel_radius() # sets radius of the wheel
        log.info("motor controller(s) initialised") #END

    async def do(self, action: Action): # NOT IN USE
        raise DeprecationWarning('use MotorController2')
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
        vx = getattr(action, 'vx', 0.)
        vy = getattr(action, 'vy', 0.)
        vw = getattr(action, 'w', 0.)

        log.debug(f"{vx=}, {vy=}, {vw=}")

        # if vx, vy and vw are all 0s, stop the motors

        # if vx < self.VELOCITY_LOWER_LIMIT and vy < self.VELOCITY_LOWER_LIMIT and vw < self.VELOCITY_LOWER_LIMIT:
        #     await self.transport.cycle(x.make_stop() for x in self.controller.values())
        #     return

        v1, v2, v3, v4 = self.calculate(vw, vx, vy) #calculate the velocity and send them back here

        query = [
            self.controllers[id+1].make_position(
                position=math.nan,
                velocity=velocity,
                query=False
            ) for id, velocity in enumerate([v1, v2, v3, v4])
        ]

        te = time.time() + self.interval
        while time.time() < te:
            # print(time.ticks_diff(time.ticks_us(), ts))
            # loop velocity
            result = await self.transport.cycle(query)

        await self._make_stop()

    def calculate(self, vx: float, vy: float, vw: float) -> np.array:
        """_summary_
            calculates omniwheels' velocities using args: vx, vy and omega
            applying the omniwheel equation from:
            
            "Modern Robotics: Mechanics, Planning & Control"
            13.2.1

        Args:
            vx (float): velocity in x direction (cm/s)
            vy (float): velocity in y direction (cm/s)
            vw (float): angle velocity (rad/s)

        Params: 
            vb (matrix (1,3)): compiles the 3 velocity into an array
            H (matrix(4,3)): applies the Omniwheel veloicty matrix
            H.T: transpose H matrix into (3,4)

        Returns:
            uv (array): returns all calculated wheel velocity
        """

        uv =  np.array([
            (1. / self.r1) * ((self.d1 * vw) - (vx * np.sin(self.b1)) + (vy * np.cos(self.b1))),
            (1. / self.r2) * ((self.d2 * vw) - (vx * np.sin(self.b2)) + (vy * np.cos(self.b2))),
            (1. / self.r3) * ((self.d3 * vw) - (vx * np.sin(self.b3)) + (vy * np.cos(self.b3))),
            (1. / self.r4) * ((self.d4 * vw) - (vx * np.sin(self.b4)) + (vy * np.cos(self.b4)))
        ])
        
        for v in uv:
            if v > self.VELOCITY_UPPER_LIMIT:
                uv = np.array([0., 0., 0., 0.])
                break

        uv = np.multiply(uv, 1/2*np.pi)
        log.debug(f"calculate({vw=}, {vx=}, {vy=}) = {uv=}")
        return uv
        
    def set_direction_of_cw_motion(self) -> None:
        """_summary_
        """
        self.b1 = np.radians(self.OMNIWHEEL_1_CW_ANGLE_DEG)
        self.b2 = np.radians(self.OMNIWHEEL_2_CW_ANGLE_DEG)
        self.b3 = np.radians(self.OMNIWHEEL_3_CW_ANGLE_DEG)
        self.b4 = np.radians(self.OMNIWHEEL_4_CW_ANGLE_DEG)

    def set_wheel_xy_location(self) -> None:
        """_summary_
            Sets the distance of each wheels from the centre using Pythagorus Theorum.
        """

        self.d1 = np.sqrt(self.OMNIWHEEL_1_XY_COORDINATES[0]**2+self.OMNIWHEEL_1_XY_COORDINATES[1]**2)/self._u
        self.d2 = np.sqrt(self.OMNIWHEEL_2_XY_COORDINATES[0]**2+self.OMNIWHEEL_2_XY_COORDINATES[1]**2)/self._u
        self.d3 = np.sqrt(self.OMNIWHEEL_3_XY_COORDINATES[0]**2+self.OMNIWHEEL_3_XY_COORDINATES[1]**2)/self._u
        self.d4 = np.sqrt(self.OMNIWHEEL_4_XY_COORDINATES[0]**2+self.OMNIWHEEL_4_XY_COORDINATES[1]**2)/self._u

    def set_wheel_radius(self) -> None:
        """_summary_
            sets radius of the wheel (applying unit scaling)
        """
        self.r1 = self.OMNIWHEEL_1_RADIUS/self._u
        self.r2 = self.OMNIWHEEL_2_RADIUS/self._u
        self.r3 = self.OMNIWHEEL_3_RADIUS/self._u
        self.r4 = self.OMNIWHEEL_4_RADIUS/self._u

    async def run(self) -> None: # NOT IN USE
        raise DeprecationWarning('use MotorController2')
        await self._make_stop()
        while True:
            try:
                self.tc_action_recv_event.wait()
                action = self.shared_global_resource.get_action()
                if not isinstance(action, Action):
                    raise TypeError(f"unexpected type: expected 'Action', got: {action.__class__}")
                log.info(f"running {action}")
                await self.do(action)
                self._tc_action_recv_event.clear()
            except KeyboardInterrupt:
                await self._exit()
            except asyncio.CancelledError:
                await self._exit()

            # power_telemetry = await self.steam.read_data("power")
            # log.info(power_telemetry)
            # self.shared_global_resource.set_voltage(power_telemetry.output_voltage_V)
            # self.shared_global_resource.set_current(power_telemetry.output_current_A)

            if self._gc_force_shutdown_event.is_set():
                break

    @staticmethod
    def add_cls_specific_arguments(parent: argparse.ArgumentParser) -> argparse.ArgumentParser:
        '''
            add_cls_specific_arguments
                adds:
                    --disable-motor-controller argument which disables the motors when set

            @args:
                parent (argparse.ArgumentParser): argparse object from run.py
            
        '''
        parser = parent.add_argument_group('MotorController')
        parser.add_argument('--disable-motor-controller', action='store_true')
        return parent
    
    async def _exit(self):
        await self._make_stop()
    
    async def _make_stop(self):
        await self.transport.cycle(x.make_stop() for x in self.controllers.values())

    @property
    def scaling(self): # scale the motor controller actions from 'mm' to something else
        return self._u
    
    @scaling.setter
    def scaling(self, u):
        if not isinstance(u, int):
            raise ValueError
        self._u = u
    
    @property
    def interval(self): # action time interval (ms)
        return self._interval
    
    @interval.setter
    def interval(self, interval):
        if not isinstance(interval, int):
            raise ValueError
        self._interval = interval

class MotorControllerFactory:
    @staticmethod
    def __call__(shared_global_resource, event, args) -> None:
        motor = MotorController(shared_global_resource)
        motor.tc_action_recv_event = event['tc_action_recv_event']
        motor.gc_force_shutdown_event = event['gc_force_shutdown_event']
        asyncio.run(motor.run())