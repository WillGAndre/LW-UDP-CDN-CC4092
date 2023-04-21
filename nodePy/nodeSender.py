import socket
import os

class Sender:
    def __init__(self):
        self.IP = "0.0.0.0"
        self.PORT = os.environ.get('PORT', 8080)

    def simpleMsg(self, msg):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(msg, (self.IP, self.PORT))

    ##def sendFile
    ##def sendCode