
class Action:
    def __init__(self, vx: float, vy: float, omega: float, kick: bool, dribble: float):
        """_summary_
            Object for initialise action commands, encode / decode strings for UDP transportation.
        Args:
            vx (float): wanted velocity for x direction
            vy (float): wanted velocity for y direction
            omega (float): wanted angular velocity (radians)
            kick (bool): wanted kicker to kick (Yes/No)
            dribble (float): dribbling speed ? 
        """
        self.vx = vx
        self.vy = vy
        self.omega = omega
        self.kick = kick
        self.dribble = dribble
    
    def encode(self):
        """_summary_
            Turns everything within the action class into a string
        Returns:
            message(string): string for send message to send
        """
        self.msg = f"{self.vx} {self.vy} {self.omega} {self.kick} {self.dribble}"
        return self.msg

    @staticmethod
    def decode(msg):
        """_summary_
            decodes the message receives upon UDP transportation.
        Args:
            msg (string): message received upon UDP

        Returns:
            Action (Object): new Action object Model for easier attribute access
        """
        vx, vy, omega, kick, dribble = msg.decode().split(" ")
        args = list(float(vx),float(vy),float(omega),bool(kick),float(dribble))
        return Action(*args)
        
    
    
    def __repr__(self): #debug msg
        return f"Action: (vx: {self.vx}, vy: {self.vy}, theta: {self.omega}, kick: {self.kick}, dribble: {self.dribble})"
    