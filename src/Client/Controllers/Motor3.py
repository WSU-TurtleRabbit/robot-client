'''re-implmentation of Motor.py for real-time response'''
from Client.Controllers.Motor import MotorController
from Client.Coms.Action import Action
import math
import time
import asyncio
import sys
import os

import logging

log = logging.getLogger()
log.setLevel(logging.NOTSET)

try:
    import moteus
except ImportError as e:
    log.warning(e)


class MotorController3(MotorController):
    def do(self):
        '''
            do() - implements BaseController do()
        '''
       
        # if vx, vy and vw are all 0s, stop the motors

        # if vx < self.VELOCITY_LOWER_LIMIT and vy < self.VELOCITY_LOWER_LIMIT and vw < self.VELOCITY_LOWER_LIMIT:
        #     await self.transport.cycle(x.make_stop() for x in self.controller.values())
        #     return

        v1, v2, v3, v4 = self.calculate(self.vx, self.vy, self.vw) # convert vx, vy and w into the velocities for each wheel to achieve the desired movement
        log.debug(f"Wheels are moving at the speed of {v1=} {v2=} {v3=} {v4=}")
        ## we can add validation here
        self.query = [
            self.controllers[id+1].make_position(
                position=math.nan,
                velocity=velocity,
                query=True
            ) for id, velocity in enumerate([v1, v2, v3, v4]) # send a velocity only command to the moetus controller
        ]
        

    async def run(self) -> None: # NOT IN USE
        await self._make_stop()
        while True:
            try:
                try:
                    action = self.shared_global_resource.get_action()
                    # check if there's a value for action and update existing
                    
                    if isinstance(action, Action) :
                        ## optional debug
                        # log.debug("New Action Received")
                        # ## check if all = 0 ?
                        # if action.vx == 0 and action.vy == 0 and action.w == 0:
                        #     self.vx = 0.
                        #     self.vy = 0.
                        #     self.vw = 0.
                        #     # if yes, make stop
                        #     log.warning("Stop Action Received")
                        #     await self._make_stop() #stopping all motors
                            
                        # elif abs(action.vx)>0 or abs(action.vy) > 0 or abs(action.w) > 0:
                            # reset fault
                        # await self._make_stop() # comment this if needed
                        # update velocity
                        self.vx = action.vx
                        self.vy = action.vy
                        self.vw = action.w
                        log.info(f"new Velocity Received : {self.vx=} {self.vy=} {self.vw=}, {self._last_action_time}")
                        # updating last sent action timer
                        self._last_action_time =  action._time 
                    
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
                    
                    log.debug(f"Action Expired Time : {self._last_action_time+self._action_interval}, time Now : {time.time()}")

                    # if the time now is still within the action time
                    if time.time() < self._last_action_time + self._action_interval:
                        # loop the action
                        logging.warning("Action is now active, moving robot")
                        self.do()
                        results = await self.transport.cycle(self.query) # send the wheel velocities to the motor controllers
                        await asyncio.sleep(0.02)
                        # for i in range(4): # each motor controller has query=True, check the registers for a fault state
                        #     mc_fault_status = results[i].values[moteus.Register.FAULT] 
                        #     if not mc_fault_status == 0:
                        #         self._make_stop() 
                    else: # if the max action timer has reached, reset.
                        logging.warning("Action Timed Out, ROBOT IDLE.")
                        # await self._make_stop()
                        
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


class MotorController3Factory:
    @staticmethod
    def __call__(shared_global_resource, event) -> None:
        '''
            MotorController2Factory()

            @args:
            shared_global_resource (TeamControl.SharedGlobalResource) interprocess communication messaging object
            event (list[multiprocessing.Event]): list of mutliprocessing.Event objects to signal the process to do various actions
        '''
        motor = MotorController3(shared_global_resource)
        motor.tc_action_recv_event = event['tc_action_recv_event'] # not in use
        motor.gc_force_shutdown_event = event['gc_force_shutdown_event'] # not in use
        asyncio.run(motor.run()) # motor controller functions are all asynchronous functions