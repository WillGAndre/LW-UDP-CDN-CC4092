import socket
import nodeSender

class Ptp:
    def __init__(self, socket):
        self.nodes = []
        self.sock = socket
        self.sender = nodeSender.Sender()

    #send PING to network
    def ping(self):
        for node in nodes:
            sender.simpleMsg(self.sock, node, "PING")    

    def handle(self, addr, msg):
        if msg.split(" ")[1] == "JOIN":
            print("-- Recieved JOIN, adding addr : %s" % addr[0])
            self.nodes.append(addr[0])
            self.sender.simpleMsg(self.sock, addr, "P2P JOIN RECIEVED")
        
        if msg.split(" ")[1] == "LIST":
            print("-- Recieved LIST, current nodes are : ".join(str(x) for x in self.nodes))
            self.sender.simpleMsg(self.sock, addr, str(self.nodes))
        
        else:
            pass