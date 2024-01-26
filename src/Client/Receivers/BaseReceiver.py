import random
import os
import time
import socket

SERVER = {}
class BaseReceiver:

    ## This func. will be triggered when an object is initiated
    def __init__(self):
        """_summary_
            Initialising Base Reciver
        """
        # 1. it will try to assign an ID
        self.id = self.get_robot_id()
        self.stop = False
        print(f"This Robot is now with ID: {self.id}")
        # 2. since the messages has to be sent as byte, we convert it into a string then bytes
        self.b_id = bytes(str(self.id).encode())
        # 3. we create a Socket for sending and receiving on the UDP Server.
        self.sock, self.ip, self.port = self.create_sock()
        # After everything has been set, the robot will start listening continuously
        self.listen()
    
    def create_sock(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        bsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        try:
            bsock.bind(("", 12342))
        except Exception as e:
            print("Error in binding Broadcast:", type(e))
            print(e)
            raise  # Raise an exception
        
        #windows
        #ip = socket.gethostbyname(socket.gethostname())
        #raspberrypi
        ip = os.popen("hostname -I").read().strip()

        isbinding = True

        while isbinding:
            try:
                port = random.randint(5000, 9000)
                sock.bind((ip, port))
                self.sock = sock
                isbinding = False
            except Exception as e:
                print("Error in binding:", e)
                pass
            finally:
                print(ip, port)

        data, addr = bsock.recvfrom(1024)
        print(data)
        SERVER["IP"], SERVER["PORT"] = data.decode().split(", ")
        print(SERVER, (SERVER["IP"], SERVER["PORT"]))
        msg = self.b_id
        self.send_message(msg)

        return sock, ip, port

    # func for send message
    # this is useful as it optimise the repetition of this line.
    def send_message(self, msg):
        # the socket will send message to the server address and port
        self.sock.sendto(msg, (SERVER["IP"], int(SERVER["PORT"])))
        # feedback on the client when the message has been sent
        print(f"{msg} has been sent")

    
    
        ## This functions provides a loop for recieving message
    def listen(self):
        # while it is active
        while not self.stop:
            data, addr = self.sock.recvfrom(1024)
            msg = data.decode()

            if msg == "ping":
                new_msg = self.b_id
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

            if new_msg != "":
                self.send_message(new_msg)


    @staticmethod
    def add_cls_specific_arguments(parent):
        return parent