import multiprocessing
import multiprocessing.connection
import socket
import sys
import time
import random
import os 
import ast

import enum
from enum import auto
# Overidding print

debug = False

def debug_print(*args, **kwargs):
    if debug:
        print(*args, **kwargs)


class UDP(enum.IntEnum):
    SOCK_BROADCAST_UDP = auto()
    SOCK_UDP = auto()

class Coms(): 
    """
    base class of receiver and sender
    provides common base functions
    """

    @staticmethod
    def init_sock(type) -> socket.socket:
        """ Initialise socket
        Initailise socket for broadcasting in UDP
        Arg = 
        UDP.SOCK_BROADCAST_UDP = broadcast
        UDP.SOCK_UDP = udp 

        Returns:
            socket.socket: returns the initailised socket
        """
        if type == UDP.SOCK_BROADCAST_UDP:
            broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            return broadcast
        elif type == UDP.SOCK_UDP: 
            udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return udp
        else : 
            raise NotImplementedError("only value UDP.SOCK_UDP or UDP.SOCK_BROADCAST_UDP is allowed")

    @staticmethod
    def obtain_sys_ip() -> str:
        """
        Obtaining system's ip address
        
        Params:
            os_system(sys.platform) =  current os_system.
        
        Raises:
            ValueError: No matching os system, cannot obtain IP, will need to input manually.

        Returns:
            ip (str): system's ip address
        """
        os_system = sys.platform
        match os_system:
            case 'win32':
                ip = socket.gethostbyname(socket.gethostname())
            case 'linux':
                ip = os.popen('hostname -I').read().strip().split(" ")[0]
            case 'darwin':
                ip = os.popen('ipconfig getifaddr en0').read().strip()
            case _:
                raise ValueError("Cannot Obtain IP, Please input ip address manually")       
        return ip
    
    @staticmethod
    def generate_port() -> int:
        port = random.randint(5000, 9000)
        debug_print("port generated")
        return port
            
    def bind_sock(self) -> bool:
        """
        Binds the socket to it's ip and a port

        Returns:
            bool: 
                returns True when binding is completed, 
                retruns false when binding failed.
                Used in Binding Loop
        """
        isbinded = False
        try: #binding with IP and Port
            if self.ip is None:
                self.ip = self.obtain_sys_ip()
            if self.port == 0: 
                port = self.generate_port()
            else: # since self.port is provided, use self.port
                port = self.port 
            
            # binds socket to ip and port
            self.sock.bind((self.ip,port))
            
            # if bind is successful, updating new port
            self.port:int = port
            isbinded = True 
        # if there is a value error : STOP     
        except ValueError as ve:
            raise ValueError("ERROR : ",ve)
            
        # if there is a socket error, probably something to do with binding, continue
        except socket.error as se:
            debug_print(f"Uable to bind at port: {port}, trying again... \nfull message : '{se}'\n ")
        
        except Exception as e: 
            raise Exception(f"Error encountered, aborting ... \n {e}")
            
        finally:
            debug_print("socket is binded : ",isbinded)
            return isbinded
    
    def close(self):
        self.sock.close()
        
    
class Receiver(Coms):
    def __init__ (self,ip: str=None, port: int=0, sock_type=UDP.SOCK_UDP,buffer_size: int=1024):
        """Receiver - init
        Initialising socket for receiving messages

        Args:
            ip (str, optional): ip of Receiver. Defaults to None. None : obtaining system ip
            port (int, optional): prefered port number. Defaults to 0: auto-generated. Otherwise, please enter a number
            sock_type (str, optional): type of socket. Defaults to 'u' - UDP. alternative: 'b' - Broadcast, see init_sock()
            buffer_size (int, optional): size for packet to be received. Defaults to 1024.
        
        Params:
            ready (bool): is socket ready to use ? True : YES, False : NO
            source(tuple[str,int]) : default sender's address, potential use for filter and verification. Currently Not implemented.
        """
        self.ip:str = ip
        self.port:int = port
        self.sock_type:str = sock_type
        self.buffer_size:int = buffer_size
        self.ready:bool = self.create()
        self.source:tuple[str,int] = None
        
    def get_addr(self)->str:
        """ Get Address
        Get the Receiver socket's address

        Returns:
            str: address tuple in the format of string
        """
        addr:tuple = (self.ip,self.port)
        return f"{addr}"
       
    def create(self) -> bool:
        """
        Creates the Socket
        Params:
            bind_success (bool): has socket binded successfully? True: Yes -> Ends Loop, False: No -> Continues Loop.
        Returns:
            bool: socket has been created : True / False -> self.ready
        """
        # initialise socket
        
        debug_print("Creating socket type : ",self.sock_type)
        self.sock:socket.socket = self.init_sock(self.sock_type)
        # starts binding
        bind_success = False
        # binds socket
        while not bind_success:
            bind_success = self.bind_sock()
        # if there's no problem, socket is now ready
        debug_print(f"{self.__class__.__name__} socket is now active on {self.ip},{self.port}")
        return bind_success # at this point it should be True
       
    def listen(self,duration: int=None)-> str|None:
        """Default Listen function
            Listening on Receiving Socket 
            *THIS IS NOT A LOOP*

        Args:
            duration (int, optional): time(second) to listen to port. Defaults to None.

        Returns:
            str : decoded data 
            or nothing.
        Raises: 
            socket.error : Socket is Not ready, please create socket again
            socket.timeout : Socket duration ended
        """
        data = None
        if not self.ready: #terminates
            raise socket.error("Error : socket needs to be created") 
        
        if duration is not None:
            self.sock.settimeout(duration)
        else:
            self.sock.settimeout(None)
        
        try:
            debug_print(f"{self.__class__.__name__} sock is now listening with buffersize : {self.buffer_size}")
            data, addr = self.sock.recvfrom(self.buffer_size)
            # data received
        except socket.timeout as to:
            #socket timeout
            debug_print("Duration ended : ",to)
            data = None
        finally:
           if data is not None: # return anything that has a value
                return self.decode(data)


    def decode(self,data:bytes) ->str|bytes:
        """Default Decode Function

        Args:
            data (bytes): Byte data received over UDP

        Returns:

            bytes: data that cannot be decoded
                or
            str: Decoded data using utf-8
        """
        try : 
            decoded_data = data.decode('utf-8')
        except UnicodeDecodeError as ude : 
            debug_print("cannot decode data, returning original. \n",ude)
            return data
        finally:
            return decoded_data
        
    def update_source(self,addr:str|tuple[str,int]):
        """
        Stores source (server or robot) sender address
        Use for verification. 

        Args:
            addr (tuple[str,int]): _description_
        """
        if isinstance(addr, str):
            addr = ast.literal_eval(addr)
        self.recv_addr = addr
        

                
class Sender(Coms):
    def __init__(self, ip: str=None, port: int=0) -> None:
        self.destination = None
        self.ip:str = ip
        self.port:int = port
        self.ready:bool = self.create()
        
    
    def create(self) -> bool:
        """Default socket creation
        Creates socket and binds sock
        Args:
            bind_success (bool): has the socket successfully binded.
        Returns:
            bool: bind success = ready to use
        """
        self.sock = self.init_sock(UDP.SOCK_UDP)
        bind_success:bool = False
        while not bind_success:
            bind_success = self.bind_sock()
        return bind_success
    
    def update_destination(self, destination:str|tuple[str,int]) -> None:
        if isinstance(destination,str):
            destination = ast.literal_eval(destination)
        self.destination = destination

    
    def send(self, msg : bytes|str,duration : int=None, destination:tuple[str,int] = None)-> None:
        """
        sends message to sender's destination

        Args:
            msg (bytes | str): the message that you want to send, can be in bytes or string format.
            duration (int, optional): How long do you want to send this message for. Defaults to None -> No repeats.
            destination (tuple[str,int],optional): Other location you want to send. Defaults to None -> use sender's destination address.

        Raises:
            AttributeError: No destination addr found. Either update sending socket, or send in a new destination.
        """
        
        if self.destination is None and destination is None:
            raise AttributeError(f"Destination : {self.destination=} | {destination=}")
        elif isinstance(destination,tuple):
            self.destination = destination
        
        # encodes message
        if isinstance(msg,str):
            msg = bytes(msg.encode('utf-8'))
        
        # if user input a duration value
        if duration is not None:
            endTime = time.time()+duration
        else :
            endTime = time.time()

        
        # reset sent boolean
        sent = False
        while not sent: # loop for sending message
            try:
                self.sock.sendto(msg,self.destination)
                sent = True
            except socket.error as se:
                debug_print(se)    
            
            finally:
                debug_print(f"message {msg.decode()} is sent to destination {self.destination}: {sent}")
                
                if endTime - time.time() <= 0:
                    debug_print("Duration ended")
                    break #exit loop
                else:
                    sent = False # try again
            
    @staticmethod    
    def encode(msg:str)-> bytes:
        try:
            msg = bytes(msg.encode('utf-8'))
        except UnicodeEncodeError:
            raise ("cannot encode message, please input a string.")
        finally:
            return msg

if __name__ ==  "__main__":
    recv = Receiver()
    sender = Sender()
    brecv = Receiver(ip = "", port = 12342,sock_type=UDP.SOCK_BROADCAST_UDP)
    
    addr = brecv.listen()
    addr = ast.literal_eval(addr)
    sender.send(recv.get_addr(),destination=addr)
    print(recv.get_addr())
    msg:str = recv.listen()
    print(msg)
    