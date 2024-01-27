# Imports 
import random
import os
import time
import socket
#from Client.Receivers.BaseReceiver import BaseReceiver
from Client.Shared.Action import Action

# Server information
SERVER = {
    "IP": "",
    "PORT": ""
}
#class UDP(BaseReceiver):
class UDP():

    ## This func. will be triggered when an object is initiated
    def __init__(self):
        """_summary_
            Initialising UDP Client Reciver
        """
        #super().__init__()

        # 1. it will try to assign an ID
        self.id = self.get_robot_id()
        self.state = "IDLE"
        print(f"This Robot is now with ID: {self.id}")
        # 2. we create a Socket for sending and receiving on the UDP Server.
        self.sock, self.ip, self.port = self.create_sock()
        # After everything has been set, the robot will start listening continuously
        self.listen()
    
    def create_sock(self):
        """_summary_
            Inits sockets for Robot Client
        Params: 
            sock (socket): socket for sending and receiving Direct UDP
            bsock (socket): socket for recieving broadcast messages
            isBinding (bool): Boolean to determine if UDP has successfully binded to IP address and port 
        Returns:
            sock, IP address and Port 
        """
        # Initialise Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        bsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # tries to bind broadcast
        try:
            bsock.bind(("", 12342))
        except Exception as e:
            print("Error in binding Broadcast:", type(e))
            print(e)
            raise  # Raise an exception
        
        ## sets IP address
        #ip = socket.gethostbyname(socket.gethostname()) #WINDOWS ONLY#
        ip = os.popen("hostname -I").read().strip() #RASPBERRY PI AND LINUX ONLY#

        isbinding = True

        while isbinding:
            try:
                port = random.randint(5000, 9000)
                sock.bind((ip, port))
                self.sock = sock
                isbinding = False
            except Exception as e:
                print("Error in binding:", e, "Trying again.")
                pass
            finally:
                print(ip, port)
        # listens to broadcast channel for the SERVER IP and PORT info
        data, addr = bsock.recvfrom(1024)
        print(data)
        SERVER["IP"], SERVER["PORT"] = data.decode().split(", ")
        print(SERVER, (SERVER["IP"], SERVER["PORT"]))
        msg = str(id)
        self.send_message(msg)

        return sock, ip, port

    
    
    def send_message(self, msg):
        """_summary_
            This function is used to encode string and sends message to the server.
        Args:
            msg (string):string of the message that you wanted to send
        """
        msg = bytes(msg.encode('utf-8'))
        # the socket will send message to the server address and port
        self.sock.sendto(msg, (SERVER["IP"], int(SERVER["PORT"])))
        # feedback on the client when the message has been sent
        print(f"Message : {msg} has been sent")

    
    
        ## This functions provides a loop for recieving message
    def listen(self):
        """_summary_
            This function is used for constant listen to the UDP socket for messages
            
        """
        # while it is active
        while self.state != "STOP":
            # enables data recieve
            data, addr = self.sock.recvfrom(1024)
            # if there is a message : decode
            msg = data.decode()

            # if the message is ping : sends the id
            if msg == "ping":
                new_msg = self.id
            else:
                try:
                    Action.decode(msg)
                    new_msg = "received"
                except Exception:
                    print("error : ", Exception)
            # else:
            #     try:
            #         # try to check the message 
            #         # the robot will be recieving the world and ball dictionary message
            #         world, ball = map(int, msg.split(",", 1))
            #         # first we wanted to know where the ball and robot is
            #         vx, vy, w = self.calculate_velocities(world, ball)

            #         # since all velocities are calculated, the ball will now move
            #         self.move()
            #         #  = map(int, msg.split(",", 3))
            #         # self.move(vx, vy, w, rt)
            #         # new_msg = "Moving"
            #     except Exception as e:
            #         print(e)
            #         raise
            
            # if we have a message to send
            if new_msg != "":
                #sends message
                self.send_message(new_msg)




    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent 
    