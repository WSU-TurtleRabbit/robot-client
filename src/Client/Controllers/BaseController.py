__all__ = []

class BaseController:
    def __init__(self):
        pass

    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent