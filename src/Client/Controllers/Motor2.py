'''re-implmentation of Motor.py for real-time response'''
from Client.Controllers.Motor import MotorController
from Client.Coms.Action import Action
import math
import time
import asyncio

import logging

log = logging.getLogger()
log.setLevel(logging.NOTSET)

try:
    import moteus
except ImportError as e:
    log.warning(e)


class MotorController2(MotorController):
    def do(self, action: Action):
        '''
            do() - implements BaseController do()
        '''
       
        vx = getattr(action, 'vx', 0.) # positive vx is the robot's forward (kicker as the front) movement
        vy = getattr(action, 'vy', 0.) # positive vy is the robots normal movement (left side of the kicker)
        vw = getattr(action, 'w', 0.) # positive w is the robots ccw spin

        log.debug(f"{vx=}, {vy=}, {vw=}")

        # if vx, vy and vw are all 0s, stop the motors

        # if vx < self.VELOCITY_LOWER_LIMIT and vy < self.VELOCITY_LOWER_LIMIT and vw < self.VELOCITY_LOWER_LIMIT:
        #     await self.transport.cycle(x.make_stop() for x in self.controller.values())
        #     return

        v1, v2, v3, v4 = self.calculate(vw, vx, vy) # convert vx, vy and w into the velocities for each wheel to achieve the desired movement

        self.query = [
            self.controllers[id+1].make_position(
                position=math.nan,
                velocity=velocity,
                query=True
            ) for id, velocity in enumerate([v1, v2, v3, v4]) # send a velocity only command to the moetus controller
        ]

    async def run(self) -> None:
        '''
            run() - overloads BaseController run()
        '''
        ts = time.time() + 0.05 # interval of action
        await self._make_stop() # clear any faults with the meotus controllers
        while True:
            try:
                action = self.shared_global_resource.get_action() 
                if not isinstance(action, Action): # if the action is invalid, stop the robot
                  log.critical(f"unexpected type: expected 'Action', got: {action.__class__}")
                  action = Action(robot_id=0)
                  await self._make_stop()
                # self._tc_action_recv_event.clear()
            except KeyboardInterrupt: # if a ctrl-c or ctrl-d interrupt is sent (via ssh), perform the _exit co-routinue 
                await self._exit()
            except asyncio.CancelledError: # catch the cancelled error just in case
                await self._exit()
        
            if time.time() < ts: # get new data from the shared global resource every internal
                if time.time() > action._time + 1000: # if the action hasn't been updated in over a second, stop the robot
                    action = Action(robot_id=0)
                self.do(action) # calculate new wheel velocities
                results = await self.transport.cycle(self.query) # send the wheel velocities to the motor controllers
                for i in range(4): # each motor controller has query=True, check the registers for a fault state
                    mc_fault_status = results[i].values[moteus.Register.FAULT] 
                    if not mc_fault_status == 0:
                        self._make_stop() 

                ts = time.time() + 0.1 # update the interval

            # power_telemetry = await self.steam.read_data("power")
            # log.info(power_telemetry)
            # self.shared_global_resource.set_voltage(power_telemetry.output_voltage_V)
            # self.shared_global_resource.set_current(power_telemetry.output_current_A)


class MotorController2Factory:
    @staticmethod
    def __call__(shared_global_resource, event) -> None:
        '''
            MotorController2Factory()

            @args:
            shared_global_resource (TeamControl.SharedGlobalResource) interprocess communication messaging object
            event (list[multiprocessing.Event]): list of mutliprocessing.Event objects to signal the process to do various actions
        '''
        motor = MotorController2(shared_global_resource)
        motor.tc_action_recv_event = event['tc_action_recv_event'] # not in use
        motor.gc_force_shutdown_event = event['gc_force_shutdown_event'] # not in use
        asyncio.run(motor.run()) # motor controller functions are all asynchronous functions