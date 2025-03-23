'''controller for replacing moteus motor controllers'''
import os
import sys
from Client.Controllers.BaseController import BaseController
from Client.Coms.Action import Action
import math
import numpy as np
import time

import asyncio
import argparse

import logging

log = logging.getLogger()
log.setLevel(logging.NOTSET)

class MotorDummy(BaseController):
    ## CLASS CONSTANT ##
    
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
        self._action_interval = 1
        self._action_duration = 0
        self.servo_bus_map: dict = { 
                    1: [1],
                    2: [2],
                    3: [3],
                    4: [4],
                    5: [32]
                }

        self.transport = self.servo_bus_map
        
        self.controllers: dict = self.servo_bus_map

        self.__set_direction_of_cw_motion() # sets wheel degrees 
        self.__set_wheel_xy_location() # sets distance to centre from each wheel
        self.__set_wheel_radius() # sets radius of the wheel
        log.info("motor controller(s) initialised") #END
    
    
    def __set_direction_of_cw_motion(self) -> None:
        """set direction of cw motion (private)
        sets each wheel's inidividual direction of CLOCKWISE Motion
        """
        self.b1 = np.radians(self.OMNIWHEEL_1_CW_ANGLE_DEG)
        self.b2 = np.radians(self.OMNIWHEEL_2_CW_ANGLE_DEG)
        self.b3 = np.radians(self.OMNIWHEEL_3_CW_ANGLE_DEG)
        self.b4 = np.radians(self.OMNIWHEEL_4_CW_ANGLE_DEG)

    def __set_wheel_xy_location(self) -> None:
        """set wheel xy location (private)
            Sets the distance of each wheels from the centre using Pythagorus Theorum.
        """

        self.d1 = np.sqrt(self.OMNIWHEEL_1_XY_COORDINATES[0]**2+self.OMNIWHEEL_1_XY_COORDINATES[1]**2)/self._u
        self.d2 = np.sqrt(self.OMNIWHEEL_2_XY_COORDINATES[0]**2+self.OMNIWHEEL_2_XY_COORDINATES[1]**2)/self._u
        self.d3 = np.sqrt(self.OMNIWHEEL_3_XY_COORDINATES[0]**2+self.OMNIWHEEL_3_XY_COORDINATES[1]**2)/self._u
        self.d4 = np.sqrt(self.OMNIWHEEL_4_XY_COORDINATES[0]**2+self.OMNIWHEEL_4_XY_COORDINATES[1]**2)/self._u

    def __set_wheel_radius(self) -> None:
        """_summary_
            sets radius of the wheel (applying unit scaling)
        """
        self.r1 = self.OMNIWHEEL_1_RADIUS/self._u
        self.r2 = self.OMNIWHEEL_2_RADIUS/self._u
        self.r3 = self.OMNIWHEEL_3_RADIUS/self._u
        self.r4 = self.OMNIWHEEL_4_RADIUS/self._u

    
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
            w (array): returns all calculated wheel velocity
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
        
    def do(self):
        v1,v2,v3,v4 = self.calculate(self.vx,self.vy,self.vw)
        print(f"Wheels are moving at the sepeed of {v1=} {v2=} {v3=} {v4=}")
        time.sleep(0.5)
        
        
        
    async def run(self) -> None: # NOT IN USE
        await self._make_stop()
        while True:
            try:
                try:
                    action = self.shared_global_resource.get_action()
                    # check if there's a value for action and update existing
                    
                    if isinstance(action, Action) :
                        ## optional debug
                        log.debug("New Action Received")
                        ## check if all = 0 ?
                        if action.vx == 0 and action.vy == 0 and action.w == 0:
                            self.vx = 0.
                            self.vy = 0.
                            self.vw = 0.
                            # if yes, make stop
                            log.warning("Stop Action Received")
                            await self._make_stop() #stopping all motors
                            
                        elif abs(action.vx)>0 or abs(action.vy) > 0 or abs(action.w) > 0:
                            # reset fault
                            # await self._make_stop() # comment this if needed
                            # update velocity
                            self.vx = action.vx
                            self.vy = action.vy
                            self.vw = action.w
                            log.info(f"new Velocity Received : {self.vx=} {self.vy=} {self.vw=}")
                            # updating last sent action timer
                            self._action_duration =  action._time +self._action_interval
                    
                    # # if received command from Team Control (server) to shut down
                    # if self._gc_force_shutdown_event.is_set():
                    #     break
                    
                    # # check if the action duration has been expired
                    # if time.time() >= self._action_duration:
                    #     log.warning("Action expired, stopping")
                    #     await self._make_stop()
                    #     self.vx,self.vy,self.vw = 0.,0.,0.
                            
                    ##if we want to do something special for NONE Action, we use the following   
                    # else: 
                    #     # log.warning(f"Action is None ")
                    #     self._make_stop()
                    #     continue #continue => skip this cycle, 
                    #     pass #pass => return to the cycle
                    

                    # if the time now is still within the action time
                    if time.time() < self._action_duration:
                        # loop the action
                        logging.warning("Action is now active, moving robot")
                        self.do()
                    else: # if the max action timer has reached, reset.
                        logging.warning("Action Timed Out, ROBOT IDLE.")
                        await self._make_stop()
                        
                # except TypeError as te: #Type error catches None in action
                    # not in use right now
                    
                # if any new unknown, we quit program and print error
                except Exception as e:
                    log.error(f"An error has occurred:\n{e}")
                    await self._make_stop()

                    sys.exit(1) 
                    # General error exit code

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

    # @staticmethod
    # def add_cls_specific_arguments(parent: argparse.ArgumentParser) -> argparse.ArgumentParser:
    #     '''
    #         add_cls_specific_arguments
    #             adds:
    #                 --disable-motor-controller argument which disables the motors when set

    #         @args:
    #             parent (argparse.ArgumentParser): argparse object from run.py
            
    #     '''
    #     parser = parent.add_argument_group('MotorController')
    #     parser.add_argument('--disable-motor-controller', action='store_true')
    #     return parent
    
    # async def _exit(self):
    #     log.info("EXITING . . .")
    #     await self._make_stop()
    
    async def _make_stop(self):
        log.info("Stopping motors")
        await asyncio.sleep(1)

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
        motor = MotorDummy(shared_global_resource)
        motor.tc_action_recv_event = event['tc_action_recv_event']
        motor.gc_force_shutdown_event = event['gc_force_shutdown_event']
        asyncio.run(motor.run())