#! /usr/bin/python3

import pygame
import os
from datetime import datetime

import asyncio

from Client.Shared.Action import Action
from Client.Controllers.Motor import Motor

def joyaxismotion(event, current_action):
    speed = 0.
    if event.value > .08:
        speed = 2.
    elif event.value < -.08:
        speed = -2.
    elif event.value > .05:
        speed = 1.
    elif event.value < -.05:
        speed = -1.
    
    match event.axis:
        case 1:   
            setattr(current_action, 'vx', speed)
        case 0:
            setattr(current_action, 'vy', speed)
        case 3:
            setattr(current_action, 'omega', speed)
            
    return current_action

def joybuttondown(event):
    match event.button:
        case 0: # A
            return Action(0., 0., 0., 1, 0.)
        case 1: # B
            pass
        case 3: # X
            pass
        case 4: # Y
            pass
    return Action(0., 0., 0., 0., 0.)

def joybuttonup(event):
    return Action(0., 0., 0., 0., 0.)
    

async def main(motor):
    await motor.transport.cycle(x.make_stop() for x in motor.servos.values())

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
        for event in pygame.event.get():
            print(f"{datetime.now().strftime('%H:%M:%S')} [EVENT] {event.type}")
            match event.type:
                case pygame.QUIT:
                    true = False

                case pygame.JOYAXISMOTION:
                    action = new_action
                    new_action = joyaxismotion(event, action)
                    
                case pygame.JOYBALLMOTION:
                    pass
                    
                case pygame.JOYBUTTONDOWN:
                    new_action = joybuttondown(event)
                    
                case pygame.JOYBUTTONUP:
                    new_action = joybuttonup(event)

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
            
            if isinstance(new_action, Action):
                print(new_action)
                motor.run(new_action)

                          
    # pygame.display.flip()
    pygame.quit()

