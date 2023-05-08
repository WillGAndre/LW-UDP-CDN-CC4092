import socket
import os
import nodeSender
import bucketControl
import threading
import ptp

class Listener:
    def __init__(self):
        self.IP = "0.0.0.0"
        self.PORT = 8080
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.IP, self.PORT))
        self.ptp = ptp.Ptp(self.sock)


        self.listen()

    
    # Server listening loop
    def listen(self):
        print("Node listening on port %s" %self.PORT)
        
        while True:
            data, addr = self.sock.recvfrom(1024)
            print('starting new thread for connection')
            thread = threading.Thread(target=self.handler, args=(data, addr))
            thread.start()

    # Handle data recieved
    def handler(self, data, addr):
        print("recieved : %s from %s" % (data , addr))

        # Create bucket control to handle commands
        bucket = bucketControl.Bucket()

        # Sender used to send messages and files.
        sender = nodeSender.Sender()
        msg = data.rstrip().decode('ASCII')

        #POSSIBLE COMMANDS
        # list insert, get, delete
        # sends success/error message with data
        #TODO return error messages

            # LOADBALANCER messages
        if (msg == "list"):
            rq = bucket.list()
            sender.simpleMsg(self.sock, addr, ("200: %s" % rq))

        elif (msg.startswith("delete")):
            #TODO check if filename is actually there
            filename = msg.split(" ")[1]
            rq = bucket.delete(filename)
            sender.simpleMsg(self.sock, addr, "200")
        elif (msg.startswith("insert")):
            #TODO wait for file to be sent in another message
            sender.simpleMsg(self.sock, addr, "ready")
        elif (msg.startswith("get")):
            #TODO get actual file and send
            filename = msg.split(" ")[1]
            sender.simpleMsg(self.sock, addr, ("getting %s" %filename ))
            
            #P2P messages
        elif (msg.startswith("P2P")):
            self.ptp.handle(addr, msg)

        else:
            sender.simpleMsg(self.sock, addr, "Command undefined")


    
