#!/usr/bin/python3 -B
import asyncio
import math
import moteus
import moteus_pi3hat
import time

async def main():
    # We will be assuming a system where there are 4 servos, each
    # attached to a separate pi3hat bus.  The servo_bus_map argument
    # describes which IDs are found on which bus.
    transport = moteus_pi3hat.Pi3HatRouter(
        servo_bus_map = {
            1:[1],
            2:[2],
            3:[3],
            4:[4],
        },
    )

    # We create one 'moteus.Controller' instance for each servo.  It
    # is not strictly required to pass a 'transport' since we do not
    # intend to use any 'set_*' methods, but it doesn't hurt.
    #
    # This syntax is a python "dictionary comprehension":
    # https://docs.python.org/3/tutorial/datastructures.html#dictionaries
    servos = {
        servo_id : moteus.Controller(id=servo_id, transport=transport)
        for servo_id in [1, 2, 3, 4]
    }

    # We will start by sending a 'stop' to all servos, in the event
    # that any had a fault.
    await transport.cycle([x.make_stop() for x in servos.values()])
    speed = 2.0
    while True:
        # The 'cycle' method accepts a list of commands, each of which
        # is created by calling one of the `make_foo` methods on
        # Controller.  The most common thing will be the
        # `make_position` method.

        now = time.time()

        # For now, we will just construct a position command for each
        # of the 4 servos, each of which consists of a sinusoidal
        # velocity command starting from wherever the servo was at to
        # begin with.
        #
        # 'make_position' accepts optional keyword arguments that
        # correspond to each of the available position mode registers
        # in the moteus reference manual.
        
        commands = [
            servos[1].make_position(
                position=math.nan,
                velocity=speed,
                query=True),
            servos[2].make_position(
                position=math.nan,
                velocity=speed,
                query=True),
            servos[3].make_position(
                position=math.nan,
                velocity=speed,
                query=True),
            servos[4].make_position(
                position=math.nan,
                velocity=speed,
                query=True),
        ]

        # By sending all commands to the transport in one go, the
        # pi3hat can send out commands and retrieve responses
        # simultaneously from all ports.  It can also pipeline
        # commands and responses for multiple servos on the same bus.
        results = await transport.cycle(commands)

        # The result is a list of 'moteus.Result' types, each of which
        # identifies the servo it came from, and has a 'values' field
        # that allows access to individual register results.
        #
        # Note: It is possible to not receive responses from all
        # servos for which a query was requested.
        #
        # Here, we'll just print the ID, position, and velocity of
        # each servo for which a reply was returned.
        print(", ".join(
            f"({result.arbitration_id} " +
            f"{result.values[moteus.Register.POSITION]} " +
            f"{result.values[moteus.Register.VELOCITY]})"
            for result in results))

        # We will wait 20ms between cycles.  By default, each servo
        # has a watchdog timeout, where if no CAN command is received
        # for 100ms the controller will enter a latched fault state.
        await asyncio.sleep(0.02)


if __name__ == '__main__':
    asyncio.run(main())
