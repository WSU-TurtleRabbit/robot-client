#! /usr/bin/env python3

import asyncio
from Client.Controllers.Motor import Motor
from Client.Shared.Action import Action

async def main():

    motor = Motor()

    await motor.transport.cycle(x.make_stop() for x in motor.servos.values())

    action = Action(1, 1, 45, False, .0)
    await motor.run(action)

    await asyncio.sleep(1.0)

asyncio.run(main())