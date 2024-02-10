from Client.Shared.Action import Action
from multiprocessing import Event

class BaseController:
    def __init__(self):
        self.event_action_is_set = Event()

    def run(self, action):
        if not isinstance(action, Action):
            raise TypeError(f"unexpected type: expected 'Action', got: {action.__class__}")
        self.action(action)
    
    def action(self, action):
        raise NotImplementedError
    
    def listen(self, namespace, event_action_is_set):        
        while True:
            if event_action_is_set.is_set():
                action = namespace.action
                event_action_is_set.clear()
                self.run(action)

    def pipe_(self):
        raise DeprecationWarning("pipe_() no longer in use.")
        from multiprocessing import Pipe
        self.recv = Pipe(duplex=False)
        return self.recv[1]
    
    def get_event(self):
        return self.event_action_is_set
        
    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent