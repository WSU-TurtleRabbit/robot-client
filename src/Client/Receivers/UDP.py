from Client.Receivers.BaseReceiver import BaseReceiver

class UDP(BaseReceiver):
    def __init__(self):
        super().__init__()

    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent 
    