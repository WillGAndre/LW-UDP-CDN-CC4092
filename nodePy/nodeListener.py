import socket
import os

class Listener:
    def __init__(self):
        self.IP = "0.0.0.0"
        self.PORT = os.environ.get('PORT', 8080)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.IP, self.PORT))
        self.listen()
    
    def listen(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            self.handler(data, addr)

    def handler(self, data, addr):
        print("recieved : %s from %s" % (data , addr))

        ##switch message (get, post, delete)

        ##call bucket control

        ##send feedback/file with nodeSender