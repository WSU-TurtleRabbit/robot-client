from Client.Shared.Action import Action
from multiprocessing import Pipe

class BaseController:
    def __init__(self):
        self.pipe = None

    def run(self, action):
        if not isinstance(action, Action):
            raise TypeError(f"unexpected type: Action, got: {action.__class__}")
        
    def listen(self):
        if not isinstance(self.pipe, tuple):
            raise Exception(f"pipe() needs to be called before listen()")
        
        while True:
            recved = self.pipe[0].recv()
            if isinstance(recved, Action):
                self.run(recved)
            # if isinstance(recved, str):
            #     self.update_state(recved)

    def pipe(self):
        if not isinstance(self.pipe, tuple):
            self.pipe = Pipe(duplex=False)
        return self.pipe[1]
    
    # def update_state(self, state):
    #     self.state = state

    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent