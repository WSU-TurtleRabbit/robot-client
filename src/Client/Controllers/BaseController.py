from Client.Shared.Action import Action

class BaseController:
    def __init__(self):
        pass

    def run(self, action):
        if not isinstance(action, Action):
            raise TypeError(f"unexpected type: Action, got: {action.__class__}")

    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent