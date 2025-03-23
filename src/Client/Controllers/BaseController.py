'''abstract controller class'''
from Client.Coms.Action import Action
from multiprocessing import Event
import argparse
import logging

log = logging.getLogger()
log.setLevel(logging.NOTSET)

class BaseController:
    def __init__(self, shared_global_resource) -> None:
        """
            initialises a controller to comunicate with robot hardware
        Params:
            event_acton_is_set (mutliprocessing.Event): event to tell process an action has been received
            recv: (multiprocessing.Pipe): deprecated
        """
        self._msg_recv_event = None
        self.shared_global_resource = shared_global_resource
    
    def do(self, action: Action) -> None:
        """
            controller's `Action` object processing method
        Args:
            action (Action): `Action` object to be processed by this controller
        """
        raise NotImplementedError()
    
    def run(self) -> None:
        while True:
            try:
                action = self.shared_global_resource.get_action()
                if not isinstance(action, Action):
                    log.critical(f"unexpected type: expected 'Action', got: {action.__class__}")
                    action = Action(robot_id=0)
                self.do(action)
                # self._msg_recv_event.clear()
            except KeyboardInterrupt:
                self._exit()
            except TypeError:
                continue
                
            if self._gc_force_shutdown_event.is_set():
                break
        
    @staticmethod
    def add_cls_specific_arguments(parent: argparse.ArgumentParser) -> None:
        return parent
    
    def _exit(self):
        ...
    
    @property
    def tc_action_recv_event(self): # NOT IN USE
        return self._tc_action_recv_event
    
    @tc_action_recv_event.setter
    def tc_action_recv_event(self, tc_action_recv_event):
        self._tc_action_recv_event = tc_action_recv_event

    @property
    def gc_force_shutdown_event(self): # NOT IN USE
        return self._gc_force_shutdown_event
    
    @gc_force_shutdown_event.setter
    def gc_force_shutdown_event(self, gc_force_shutdown_event):
        self._gc_force_shutdown_event = gc_force_shutdown_event
