import asyncio
from Client.Controllers.Motor import Motor
from Client.Receivers.UDP import UDP

async def main():

    motor = Motor()

    await motor.transport.cycle(x.make_stop() for x in motor.servos.values())
    
    udp = UDP()

    #await motor.run(action)

    #await asyncio.sleep(1.0)

asyncio.run(main())