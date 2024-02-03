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
        Params: 
            id (int) : Robot Client's ID
            server (tuple) : the server's UDP address (ip, port)
            ip (str) : Robot's ip address
            port (int) : Robot's port number
            bsock (socket) : Robot's Broadcast Channel (receive only)
            sock (socket) : Robot's UDP Channel (send and receive)
            state (str) : determines the state of Robot Client
        """
        self.id = None
        self.server = tuple()
        self.ip = None
        self.port = None
        self.bsock = None
        self.sock = None
        self.state = "IDLE"


        self.create_sock() # Initialising Sockets.
        self.listen_broadcast() # can be put as part of multiprocessing
        #self.listen_udp()
        
       # self.listen()
    
    def create_sock(self):
        """_summary_
            Initialise sockets - Broadcast and UDP Channels.
            These 
        Params: 
            sock (socket): socket for sending and receiving Direct UDP
            bsock (socket): socket for recieving broadcast messages 
            bind_success (bool): Boolean to determine if UDP has successfully binded to IP address and port 
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
        self.ip = socket.gethostbyname(socket.gethostname()) #WINDOWS ONLY#
        if(sys.platform == 'linux'):
            self.ip = os.popen("hostname -I").read().strip().split(" ")[0] #RASPBERRY PI AND LINUX ONLY#

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
    
    def send_message(self, msg):
        """_summary_
            This function is used to encode string into bytes, then sends message to the server.
        Args:
            msg (string):string of the message that you wanted to send
        """
        if self.id != None:
            msg = f"{self.id}, {msg}"
            print(msg)
        msg = bytes(msg.encode('utf-8'))
        # the socket will send message to the server address and port
        self.sock.sendto(msg,self.server)
        # feedback on the client when the message has been sent
        print(f"Message : {msg} has been sent")

    def listen_udp(self,queue):
        """_summary_
            This function is used to trigger the listening event of UDP Server during 
            Robot state = ACTIVE
            
            Queue from multiprocessing needs to be passed in to queue Actions for future process

        Args: 
            queue(Queue) : the queue of actions
        Params:
            data (bytes): UDP (byte) message received from server directly  
            msg_rec(str) : decoded data
            msg_rep(str) : messages to be sent to the server
            new_action(str) : Action string received from server
        """

        while self.state == "ACTIVE":
            msg_rec = None
            msg_rep = None 
            data, addr = self.sock.recvfrom(1024)
            msg_rec = data.decode()
            print(f"new_message received : {msg_rec}")
            if self.id ==None:
                self.id = int(msg_rec)
                #self.send_message(f"id assigned {self.id}")
                print(f"This robot is now id : {self.id}")
            elif type(msg_rec) is str:
                try:
                    new_action = Action.decode(msg_rec)
                    # print(new_action)
                    if not queue.full():
                        queue.put(new_action)
                        msg_rep = "Action Added"
                    else:
                        print(f"error: queue full; {new_action} was dropped")
                        msg_rep = "Action Full, dropped"
                    self.send_message(msg_rep)
                except Exception:
                    print("error : ", Exception)
                # else:
        #drop queue here

    def listen_broadcast(self):
        """_summary_
            This is used to receive broadcast messages from the server
        """
        while self.state != "DEAD":            
            msg = None
            data, addr = self.bsock.recvfrom(1024)
            cmd = data.decode()
            if isinstance(eval(cmd),tuple) and self.id == None:
                self.server = eval(cmd)
                print(self.server)
                msg = "new"
                self.state = "ACTIVE" #START UDP LISTENER
            elif cmd == "ping":
                msg = self.id
            elif cmd =="stop":
                self.state = "STOP"
                msg = "stop"
                #drop queue here ?
            elif cmd =="start" :
                self.state = "ACTIVE"
                msg = "start"
            if msg != None:
                self.send_message(msg)
                return #debug purposes

        ## This functions provides a loop for recieving message
    def listen(self, queue):
        raise DeprecationWarning('listen() is deprecated, use listen_udp() and listen_broadcast()')
        """
            Function no longer in use - replaced by "listen_udp" and "listen_broadcast"
        """
        return None

        
    
    def get_id(self):
        return self.id
    
    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent 
    