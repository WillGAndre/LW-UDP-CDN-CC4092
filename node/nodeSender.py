import socket
import os

class Sender:
    def simpleMsg(self, sock, addr, msg):
        print("sending " + str(msg) +"to " + addr[0] +":" + str(addr[1]))
        
        sock.sendto((msg +"\n").encode(), addr)

    #TODO sendFile
    #TODO sendCode