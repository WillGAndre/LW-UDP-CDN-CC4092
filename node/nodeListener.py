import socket
import os
import nodeSender
import bucketControl

class Listener:
    def __init__(self):
        self.IP = "0.0.0.0"
        self.PORT = os.environ.get('PORT', 8080)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.IP, self.PORT))
        self.listen()
    
    def listen(self):
        print("waiting on recieve")
        while True:

            data, addr = self.sock.recvfrom(1024)
            self.handler(data, addr)

    def handler(self, data, addr):
        print("recieved : %s from %s" % (data , addr))

        bucket = bucketControl.Bucket()
        sender = nodeSender.Sender()

        ##todo if error
        print(str(data), str(data).startswith("b'delete"))
        if (data == b'list\n'):
            data = bucket.list()
            sender.simpleMsg(self.sock, addr, ("200: %s\n" % data).encode())
        elif (str(data).startswith("b'delete")):
            #todo delete filename
            #data = bucket.delete()
            sender.simpleMsg(self.sock, addr, "200\n".encode())

            # case "insert":
            #     sender.simpleMsg(self.sock, addr, "")
            # case "get":
            
            # case "delete"
        else:

            sender.simpleMsg(self.sock, addr, "Command undefined\n".encode())


    
