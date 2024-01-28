#! /usr/bin/python3

import pygame
import os
from datetime import datetime

import asyncio

from Client.Shared.Action import Action
from Client.Controllers.Motor import Motor

async def main(motor):
    await motor.transport.cycle(x.make_stop() for x in motor.servos.values())

async def run(motor, action):
    await motor.run(action)

if __name__ == '__main__':
    os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = "1"
    motor = Motor()
    asyncio.run(main(motor))
    pygame.init()
    

    # display = pygame.display.set_mode((100, 100))
    # clock = pygame.time.Clock()

    joysticks = {}
    new_action = Action(0., 0., 0., 0., 0.)
    true = True
    while true:
        joyaxismotion = []
        for event in pygame.event.get():
            # print(f"{datetime.now().strftime('%H:%M:%S')} [EVENT] {event.type}")
            match event.type:
                case pygame.QUIT:
                    true = False

                case pygame.JOYAXISMOTION:
                    if event.value > 0.5 or event.value < -0.5:
                        joyaxismotion.append(event)
                    
                case pygame.JOYBALLMOTION:
                    pass
                    
                case pygame.JOYBUTTONDOWN:
                    pass
                    
                case pygame.JOYBUTTONUP:
                    pass

                case pygame.JOYHATMOTION:
                    pass

                case pygame.JOYDEVICEADDED:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joysticks[joystick.get_instance_id()] = joystick
                    joystick.init()
                    print(f"{joystick.get_name()}")
                 
                case pygame.JOYDEVICEREMOVED:
                    del joysticks[event.instance_id]
                    print(f"{event.instance_id}")
       
        if len(joyaxismotion) > 0:
            print(joyaxismotion) 

                          
    # pygame.display.flip()
    pygame.quit()

