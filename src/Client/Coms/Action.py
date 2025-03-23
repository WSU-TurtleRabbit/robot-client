import time
from abc import ABC,abstractmethod
import logging

log = logging.getLogger()

class BaseAction(ABC):
    def __init__(self) -> None:
        super().__init__()
        
    @abstractmethod
    def encode(self):
        ...
        
    @abstractmethod
    def decode(self):
        ... 
    
class Action(BaseAction):
    def __init__(self, robot_id:int, vx: float = 0.0, vy: float = 0.0, w: float = 0.0, kick: int = 0, dribble: bool = False):
        """Action
            Object for initialise action commands, encode / decode strings for UDP transportation.
        Args:
            robot_id (int) : wanted Robot ID
            vx (float): wanted velocity for x direction
            vy (float): wanted velocity for y direction
            w (float): wanted angular velocity (radians)
            kick (int): wanted kicker to kick (0/1)
            dribble (int): wanted kicker to dribble (0/1)
            
        Params:
            time(time.time): time of packet generated
        """
        self._time: float = time.time()
        self._robot_id: int = robot_id
        self._vx: float = vx
        self._vy: float = vy
        self._w: float = w
        self._kick: int = kick
        self._dribble: int = dribble
    
    def id(self) -> int:
        """Gets the robotID of action

        Returns:
            int: Robot ID
        """
        return self.robot_id
    
    def encode(self) -> bytes:
        """encode
            Encodes action object into bytes
            
        Returns:
            bytes: byte data for sending
        """
        self.msg = f"{self._robot_id} {self._vx} {self._vy} {self._w} {self._kick} {self._dribble} {self._time}"
        self.msg = bytes(self.msg.encode('utf-8'))
        return self.msg
    
    @classmethod
    def decode(cls,action_string:str) -> object:
        """decode
            decode and stores the action to an object
        Args:
            action (bytes): message received upon UDP
            
        Params: 
            args (arguments): list of arguments to be parsed into creating an Action Object

        Returns:
            object: Action object for robot to access
        """
        if isinstance(action_string, bytes):
            action_string = action_string.decode()

        robot_id, vx, vy, w, kick, dribble, _time = action_string.split(" ")
        
        args = [int(robot_id), float(vx),float(vy),float(w),int(kick),int(dribble)]
        
        return Action(*args) 

    def __repr__(self) -> str:
        """ this is a representation statement
        
        Returns:
            str: representation string
        """ 
        return f"Action: (id: {self._robot_id} vx: {self._vx}, vy: {self._vy}, theta: {self._w}, kick: {self._kick}, dribble: {self._dribble}), time: {self._time}"
    
    @property
    def robot_id(self):
        return self._robot_id
    
    @robot_id.setter
    def robot_id(self, robot_id: int):
        if not isinstance(robot_id, int):
            raise ValueError
        self._robot_id = robot_id

    @property
    def w(self):
        return self._w
    
    @w.setter
    def w(self, w: float):
        if not isinstance(w, float):
            raise ValueError
        self._w = w

    @property
    def vx(self):
        return self._vx
    
    @vx.setter
    def vx(self, vx: float):
        if not isinstance(vx, float):
            raise ValueError
        self._vx = vx


    @property
    def vy(self):
        return self._vy
    
    @vy.setter
    def vy(self, vy: float):
        if not isinstance(vy, float):
            raise ValueError
        self._vy = vy
    
    @property
    def kick(self):
        return self._kick
    
    @kick.setter
    def kick(self, kick: int):
        if not isinstance(kick, int):
            raise ValueError
        self._kick = kick
    
    @property
    def dribble(self):
        return self._dribble
    
    @dribble.setter
    def dribble(self, dribble: int):
        if not isinstance(dribble, int):
            raise ValueError
        self._dribble = dribble

    
