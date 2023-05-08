import socket
import os

class Sender:
    def __init__(self):
        self.IP = "0.0.0.0"
        self.PORT = os.environ.get('PORT', 8080)

    def simpleMsg(self, sock, addr, msg):
        print("sending " + str(msg) +"to " + addr[0] +":" + str(addr[1]))
        
        sock.sendto(msg, addr)

    #TODO sendFile
    #TODO sendCode