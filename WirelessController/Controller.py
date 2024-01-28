#! /usr/bin/python3

import pygame
import os
import time
import datetime

from Client.Shared.Action import Action

# def joydevicecheck():
#     joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
#     print(f"{time.time()}: pygame.joystick.get_count() returned {len(joysticks)}")
#     for joystick in joysticks:
#         joystick.init()
#         print(joystick.get_name())
#     return joysticks

if __name__ == '__main__':
    os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = "1"
    pygame.init()

    display = pygame.display.set_mode((100, 100))
    clock = pygame.time.Clock()

    joysticks = {}

    true = True
    while true:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    true = False
                case pygame.JOYAXISMOTION:
                    print(f"[EVENT] JOYAXISMOTION")
                    print(event)
                    
                case pygame.JOYBALLMOTION:
                    print(f"[EVENT] JOYBALLMOTION")
                    
                case pygame.JOYBUTTONDOWN:
                    print(f"[EVENT] JOYBUTTONDOWN")
                    
                case pygame.JOYBUTTONUP:
                    print(f"[EVENT] JOYBUTTONUP")

                case pygame.JOYHATMOTION:
                    print(f"[EVENT] JOYHATMOTION")

                case pygame.JOYDEVICEADDED:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    joysticks[joystick.get_instance_id()] = joystick
                    joystick.init()
                    print(f"[EVENT] JOYDEVICEADDED - {joystick.get_name()}")
                 
                case pygame.JOYDEVICEREMOVED:
                    del joysticks[event.instance_id]
                    print(f"[EVENT] JOYDEVICEREMOVED - {event.instance_id()}")

    pygame.display.flip()
    pygame.quit()

