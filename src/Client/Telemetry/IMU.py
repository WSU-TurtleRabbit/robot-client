from Client.Telemetry.BaseTelemetry import BaseTelemetry

import moteus
import moteus_pi3hat
import asyncio

class IMU(BaseTelemetry):
    def __init__(self):
        super().__init__()

        self.transport = moteus_pi3hat.Pi3HatRouter()

    async def run(self):
        while True:
            result = await self.transport.cycle([], request_attitude=True)
            result = [
                x for x in result if x.id == -1 and isinstance(x, moteus_pi3hat.CanAttitudeWrapper)
            ][0]

            print(result)

            await asyncio.sleep(.5)