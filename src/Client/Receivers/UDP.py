# Imports 
import random
import os
import time
import socket
#from Client.Receivers.BaseReceiver import BaseReceiver
from Client.Shared.Action import Action

import sys

# Server information
c = time.localtime()
Time= time.strftime("%H:%M:%S",c)
#class UDP(BaseReceiver):
class UDP():

    ## This func. will be triggered when an object is initiated
    def __init__(self):
        """_summary_
            Initialising UDP Client Reciver
        """
        #super().__init__()

        # 1. it will try to assign an ID
        # 2. we create a Socket for sending and receiving on the UDP Server.
        self.create_sock()
        # self.id = self.get_robot_id()
        
        self.state = "ACTIVE"
       
        # After everything has been set, the robot will start listening continuously
        # self.listen()
    
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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.bsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # tries to bind broadcast
        try:
            self.bsock.bind(("", 12342))
        except Exception as e:
            print("Error in binding Broadcast:", type(e))
            print(e)
            raise  # Raise an exception
        
        ## sets IP address
        # match sys.platform:
        # case 'win':
        # ip = socket.gethostbyname(socket.gethostname()) #WINDOWS ONLY#
        # case 'linux':
        ip = os.popen("hostname -I").read().strip() #RASPBERRY PI AND LINUX ONLY#
        self.ip = ip.split(" ")[0]

        bind_success = False

        while not bind_success:
            try:
                self.port = random.randint(5000, 9000)
                self.addr = tuple([self.ip, self.port])
                self.sock.bind(self.addr)
                print(f"Your address is : {self.addr}")

                bind_success = True
            except Exception as e:
                print("Error in binding:", e, "Trying again.")
                pass
            finally:
                print("Socket Binded : ", bind_success)
        # listens to broadcast channel for the SERVER IP and PORT info
        data, addr = self.bsock.recvfrom(1024)
        self.server = eval(data.decode())
        print(self.server)
        msg = "I am new"
        self.send_message(msg)
        data, addr = self.sock.recvfrom(1024)
        self.id = data.decode()
        print("New ID :", self.id)
    
    def send_message(self, msg):
        """_summary_
            This function is used to encode string and sends message to the server.
        Args:
            msg (string):string of the message that you wanted to send
        """
        msg = bytes(msg.encode('utf-8'))
        print(type(self.server), self.server)
        # the socket will send message to the server address and port
        self.sock.sendto(msg,self.server)
        # feedback on the client when the message has been sent
        print(f"Message : {msg} has been sent")

    
    def broadcast_listen(self):
        data, addr = self.bsock.recvfrom(1024)
        cmd = data.decode()
        if cmd == "ping":
            msg = self.id
        elif cmd =="stop":
            self.state = "STOP"
            msg = "stop"
            #drop queue here
        elif cmd =="start" :
            self.state = "ACTIVE"
            msg = "start"
        if msg != "":
            self.send_message(msg)
            msg = ""

        ## This functions provides a loop for recieving message
    def listen(self, queue):
        """_summary_
            This function is used for constant listen to the UDP socket for messages
            
        """
        # while it is active
        while self.state != "STOP":
            # enables data recieve
            data, addr = self.sock.recvfrom(1024)
            # if there is a message : decode
            msg = data.decode()

            # # if the message is ping : sends the id
            # if msg == "ping":
            #     new_msg = self.id
            # else:
            try:
                new_action = Action.decode(msg)
                # print(new_action)
                if not queue.full():
                    queue.put(new_action)
                else:
                    print(f"error: queue full; {new_action} was dropped")
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
    
    def get_id(self):
        return self.id
    
    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent 
    