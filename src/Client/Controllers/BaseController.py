from Client.Shared.Action import Action
from multiprocessing import Pipe

class BaseController:
    def __init__(self):
        self.recv = None

    def run(self, action):
        if not isinstance(action, Action):
            raise TypeError(f"unexpected type: expected 'Action', got: {action.__class__}")
        self.action(action)
    
    def action(self, action):
        raise NotImplementedError
    
    def listen(self):        
        while True:
            recved = self.recv[0].recv()
            if isinstance(recved, Action):
                self.run(recved)
            # if isinstance(recved, str):
            #     self.update_state(recved)

    def pipe(self):
        self.recv = Pipe(duplex=False)
        return self.recv[1]
    
    # def update_state(self, state):
    #     self.state = state

    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent