from Client.Shared.Action import Action
from multiprocessing import Event

class BaseController:
    def __init__(self):
        self.event_action_is_set = Event()
        self.recv = None

    def run(self, action):
        # check if action is an `Action.Action`
        if not isinstance(action, Action):
            raise TypeError(f"unexpected type: expected 'Action', got: {action.__class__}")
        # talk to the hardware
        self.action(action)
    
    def action(self, action):
        raise NotImplementedError()
    
    def listen(self, namespace):
        while True:
            # wait for mutliprocessing.Event `event_action_is_set`
            # to be set by another process 
            if self.event_action_is_set.is_set():
                # get Action `action` from shared namespace
                action = namespace.action
                # stop blocking process that set `event_action_is_set`
                self.event_action_is_set.clear()
                self.run(action)

    def pipe(self):
        from multiprocessing import Pipe
        self.recv = Pipe(duplex=False)
        return self.recv[1]
    
    def get_event(self):
        raise DeprecationWarning("get_event() no longer in use.")
        return self.event_action_is_set
        
    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent