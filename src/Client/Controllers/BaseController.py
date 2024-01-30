from Client.Shared.Action import Action
from multiprocessing import Pipe

class BaseController:
    def __init__(self):
        self.recv = None

    def run(self, action):
        if not isinstance(action, Action):
            raise TypeError(f"unexpected type: Action, got: {action.__class__}")
        
    def listen(self):
        assert self.recv is not None, "pipe() needs to be called before listen()"
        while True:
            action = self.recv.recv()
            self.run(action)

    def pipe(self):
        self.recv, _ = Pipe(duplex=False)
        return _


    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent