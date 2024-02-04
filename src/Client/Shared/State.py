from Client.Controllers.BaseController import BaseController

class State:
    def __init__(self):
        self.state = "BROADCAST"
        self.controllers = []
        self.states = ['BROADCAST', 'UDP', 'ACTIVE', 'PAUSED', 'STOP', 'FAULT']

    def update_state(self, state):
        if not state in self.states:
            self.state = 'FAULT'
            raise UserWarning(f"invalid state: {state}")
        
        self.state = state
        # for controller in self.controllers:
        #     controller.update_state(self.state)

    def get_states(self):
        return self.states

    def get_current_state(self):
        return self.state

    def add_controller(self, controller):
        if not issubclass(controller, BaseController):
            raise UserWarning(f"invalid controller: {controller.__class__} is not a subclass of {BaseController.__class__}")
        self.controllers.append(controller)
