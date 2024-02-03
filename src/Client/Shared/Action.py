#! /usr/bin/env python3 -B

class Action:
    def __init__(self, id: int, vx: float, vy: float, vw: float, kick: int, dribble: float):
        """_summary_
            Object for initialise action commands, encode / decode strings for UDP transportation.
        Args:
            id (int): client to control
            vx (float): wanted velocity for x direction
            vy (float): wanted velocity for y direction
            vw (float): wanted angular velocity (radians)
            kick (bool): wanted kicker to kick (1=True,0=False)
            dribble (float): dribbling speed ? 
        """
        self.id = int(id)
        self.vx = float(vx)
        self.vy = float(vy)
        self.vw = float(vw)
        self.kick = int(kick)
        self.dribble = float(dribble)
    
    def encode(self):
        """_summary_
            Turns everything within the action class into a string
        Returns:
            message(string): string for send message to send
        """
        self.msg = f"{self.id} {self.vx} {self.vy} {self.vw} {self.kick} {self.dribble}"
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
        id, vx, vy, vw, kick, dribble = msg.split(" ")
        print(msg)
        args = [int(id), float(vx), float(vy), float(vw), int(kick), float(dribble)]
        return Action(*args)
    
    def __repr__(self): #debug msg
        return f"Action: (id: {self.id}) (vx: {self.vx}, vy: {self.vy}, theta: {self.vw}, kick: {self.kick}, dribble: {self.dribble})"
    

if __name__ == '__main__':
    action = Action(1, 1.0, 1.0, 1.0, True, 0.0)
    print(action)
    message = action.encode()

    message = bytes(message.encode('utf-8'))
    action = Action.decode(message)
    print(action)