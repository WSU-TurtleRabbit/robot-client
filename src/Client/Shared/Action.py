
class Action:
    def __init__(self, vx: float, vy: float, omega: float, kick: bool, dribble: float):
        self.vx = vx
        self.vy = vy
        self.omega = omega
        self.kick = kick
        self.dribble = dribble

    @classmethod
    def decode(cls): 
        pass
    
    @classmethod
    def encode(cls):
        pass

    def __repr__(self):
        return f"Action: (vx: {self.vx}, vy: {self.vy}, theta: {self.omega}, kick: {self.kick}, dribble: {self.dribble})"
    