
class Action:
    def __init__(self, vx: float, vy: float, theta: float, kick: bool, dribble: float):
        self.vx = vx
        self.vy = vy
        self.theta = theta
        self.kick = kick
        self.dribble = dribble

    def __repr__(self):
        return f"Action: (vx: {self.vx}, vy: {self.vy}, theta: {self.theta}, kick: {self.kick}, dribble: {self.dribble})"