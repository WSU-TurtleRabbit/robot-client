from multiprocessing import Pipe

class BaseTelemetry:
    def __init__(self):
        self.pipe = None

    def pipe(self):
        if not isinstance(self.pipe, tuple):
            self.pipe = Pipe(duplex=False)
        return self.pipe[0]