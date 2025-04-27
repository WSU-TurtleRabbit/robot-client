'''controller for moteus motor controllers'''
from Client.Controllers.BaseController import BaseController
from Client.Coms.Action import Action
import math

import numpy as np
import time

import asyncio
import argparse
import sys 
import os

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

    def __init__(self) -> None:
        """_summary_
            initiate the motor controller with Moteus and Moteus pi3hat
        Params : 
            timeout(float) : standard values for await
            u(int) : unit scaler - used for scaling, input: mm(1) to cm(10) to m (1000)
            servo_bus_map (dict) : maps pi3hat-fdcan id to moteus boards
            transport(pi3hat-router): applys the map onto the pi3hat and initialise
            servos(map) : establish connection of moteus boards and pi3hat
        """

        # super().__init__(shared_global_resource)

        self._interval: float = 1 # ms
        self._u: float = 1. # motor movement is in 'mm' can be scaled by changing self.u
        self.vx: float = 0.
        self.vy: float = 0.
        self.vw: float = 0.
        self._action_interval = 0.2 # second
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

    async def do(self, action): #   
        """_summary_
            runs the action (moving) applying to wheels


        Args:
            action (Action): from action script import action string (vx,vy,omega)
        Params:
            cmd (dict): complies the motor make position command into a dictionary
            end (timer): sets timer for continuous runtime.
            results(complier) : runs the compiler (cmd) applies to all moteus boards via self.transport
        """
        # if vx, vy and vw are all 0s, stop the motors

        # if vx < self.VELOCITY_LOWER_LIMIT and vy < self.VELOCITY_LOWER_LIMIT and vw < self.VELOCITY_LOWER_LIMIT:
        #     await self.transport.cycle(x.make_stop() for x in self.controller.values())
    
        # print(action.vx, action.vy, action.w)
        #     return



        v1, v2, v3, v4 = self.calculate(action.vx, action.vy, action.w) # convert vx, vy and w into the velocities for each wheel to achieve the desired movement
        log.debug(f"Wheels are moving at the speed of {v1=} {v2=} {v3=} {v4=}")
        ## we can add validation here
        self.query = [
            self.controllers[id+1].make_position(
                position=math.nan,
                velocity=velocity,
                query=True
            ) for id, velocity in enumerate([v1, v2, v3, v4]) # send a velocity only command to the moetus controller
        ]
       
        

        te = time.time() + self.interval
        while time.time() < te:
            # print(time.ticks_diff(time.ticks_us(), ts))
            # loop velocity
            result = await self.transport.cycle(self.query)
            await asyncio.sleep(0.05)
            temp = []
            voltage = []
            for data in result:
                try:
                    temp_reading = data.values[moteus.Register.TEMPERATURE]
                    volatge_reading = data.values[moteus.Register.VOLTAGE]
                    temp.append(temp_reading)
                    voltage.append(volatge_reading )
                except KeyError as e:
                    log.warning("Registers cannot be found")
                    continue
            

        avg_temp = sum(temp) / len(temp)
        avg_voltage = sum(voltage) / len(voltage)
        
        tel_data = [avg_voltage, avg_temp]
        
        return tel_data
    

    async def do_v2(self, action): #   
        """_summary_
           version 2 of do function


        Args:
            action (Action): from action script import action string (vx,vy,omega)
        Params:
            cmd (dict): complies the motor make position command into a dictionary
            end (timer): sets timer for continuous runtime.
            results(complier) : runs the compiler (cmd) applies to all moteus boards via self.transport
        """
        # if vx, vy and vw are all 0s, stop the motors

        # if vx < self.VELOCITY_LOWER_LIMIT and vy < self.VELOCITY_LOWER_LIMIT and vw < self.VELOCITY_LOWER_LIMIT:
        #     await self.transport.cycle(x.make_stop() for x in self.controller.values())
    
        # print(action.vx, action.vy, action.w)
        #     return



        v1, v2, v3, v4 = self.calculate(action.vx, action.vy, action.w) # convert vx, vy and w into the velocities for each wheel to achieve the desired movement
        log.debug(f"Wheels are moving at the speed of {v1=} {v2=} {v3=} {v4=}")
        ## we can add validation here
        self.query = [
            self.controllers[id+1].make_position(
                position=math.nan,
                velocity=velocity,
                query=True
            ) for id, velocity in enumerate([v1, v2, v3, v4]) # send a velocity only command to the moetus controller
        ]
       
        

        loop_count = 2

        for i in range(loop_count):
        # print(time.ticks_diff(time.ticks_us(), ts))
        # loop velocity
            result = await self.transport.cycle(self.query)
            temp = []
            voltage = []
            for data in result:
                try:
                    temp_reading = data.values[moteus.Register.TEMPERATURE]
                    volatge_reading = data.values[moteus.Register.VOLTAGE]
                    temp.append(temp_reading)
                    voltage.append(volatge_reading )
                except KeyError as e:
                    log.warning("Registers cannot be found")
                    continue
            await asyncio.sleep(0.01)
            

        avg_temp = sum(temp) / len(temp)
        avg_voltage = sum(voltage) / len(voltage)
        
        tel_data = [avg_voltage, avg_temp]
        
        return tel_data    


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
        await self._make_stop()
        while True:
            try:
                try:
                    action = self.shared_global_resource.get_action()
                    # check if there's a value for action and update existing
                    
                    if isinstance(action, Action) :
                        # update the 3 velocity from the action
                        self.vx = action.vx
                        self.vy = action.vy
                        self.vw = action.w
                        log.info(f"new Velocity Received : {self.vx=} {self.vy=} {self.vw=}, {self._last_action_time}")
                        # updating last sent action timer
                        self._last_action_time =  action._time 
                      
                    log.debug(f"Action Expired Time : {self._last_action_time+self._action_interval}, time Now : {time.time()}")

                    # if the time now is still within the action time
                    if time.time() < self._last_action_time + self._action_interval:
                        # loop the action
                        logging.warning("Action is now active, moving robot")
                        self.do()
                        tel_data = await self.transport.cycle(self.query) # send the wheel velocities to the motor controllers
                        print(tel_data) # telemetry output
                        await asyncio.sleep(0.02)
                        
                    else: # if the max action timer has reached, reset.
                        logging.warning("Action Timed Out, ROBOT IDLE.")
                        await self._make_stop()
                        
                # except TypeError as te: #Type error catches None in action
                    # not in use right now
                    
                # if any new unknown, we quit program and print error
                except Exception as e:
                    log.error(f"An error has occurred:\n{e}")
                    await self._make_stop()

                    sys.exit(1) # General error exit code
                    
            except asyncio.exceptions.CancelledError as ce:
                log.error("cancelled error")
                sys.exit(130)
                
            except KeyboardInterrupt:
                log.warning("Keyboard Interrupt Detected, shutting down")
                log.warning("Please wait until we stop all motors")
                try:
                    await self._make_stop() #maybe comment this 
                    sys.exit(130)
                except SystemExit:
                    log.warning("PLEASE BE PATIENT! Stopping all motors...")
                    await self._make_stop()
                    os._exit(130)

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
        if not isinstance(interval, float):
            raise ValueError
        self._interval = interval

class MotorControllerFactory:
    @staticmethod
    def __call__(shared_global_resource, event) -> None:    
        ''' MotorControllerFactory()

            @args:
            shared_global_resource (TeamControl.SharedGlobalResource) interprocess communication messaging object
            event (list[multiprocessing.Event]): list of mutliprocessing.Event objects to signal the process to do various actions
        '''
        motor = MotorController(shared_global_resource)
        motor.tc_action_recv_event = event['tc_action_recv_event'] # not in use
        motor.gc_force_shutdown_event = event['gc_force_shutdown_event'] # not in use
        asyncio.run(motor.run())