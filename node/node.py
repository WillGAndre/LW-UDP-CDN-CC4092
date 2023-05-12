import requests
import sys
import socket
import os
import threading
from google.cloud import storage
import uuid

class Listener:
    def __init__(self, node):
        self.node = node
        self.sock = node.sock
        self.ptp = Ptp(self.sock)

        threading.Thread(target=self.listen).start()

    

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    # Server listening loop
    def listen(self):
        print("Node listening on port %s" %self.node.PORT)
        
        while True:
            data, addr = self.sock.recvfrom(1024)
            thread = threading.Thread(target=self.handler, args=(data, addr))
            thread.start()

    # Handle data recieved
    def handler(self, data, addr):
        print("recieved : %s from %s" % (data , addr))

        # Create bucket control to handle commands
        bucket = Bucket()

        # Sender used to send messages and files.
        sender = Sender()
        msg = data.rstrip().decode('ASCII')
        msg = msg.split(":")
        #POSSIBLE COMMANDS
        # list insert, get, delete
        # sends success/error message with data
        #TODO return error messages

            # LOADBALANCER messages
        if (msg[0] == "list"):
            rq = bucket.list()
            sender.simpleMsg(self.sock, addr, ("200: %s" % rq))

        elif (msg[0] == "delete"):
            #TODO check if filename is actually there
            filename = msg.split(" ")[1]
            rq = bucket.delete(filename)
            sender.simpleMsg(self.sock, addr, "200")
        elif (msg[0] == "insert"):
            #TODO wait for file to be sent in another message
            sender.simpleMsg(self.sock, addr, "ready")
        elif (msg[0] == "get"):
            #TODO get actual file and send
            filename = msg.split(" ")[1]
            sender.simpleMsg(self.sock, addr, ("getting %s" %filename ))
            
            #P2P messages
        elif (msg[0] == "P2P"):
            self.ptp.handle(addr, msg)


    
class Sender:
    def simpleMsg(self, sock, addr, msg):
        print("sending : " + str(msg) +" to " + addr[0] +":" + str(addr[1]))
        
        sock.sendto((msg +"\n").encode(), addr)

    #TODO sendFile
    #TODO sendCode


class Ptp:
    def __init__(self, socket):
        self.nodes = []
        self.sock = socket
        self.sender = Sender()

    #send PING to network
    def ping(self):
        for node in nodes:
            sender.simpleMsg(self.sock, node, "PING")    

    def handle(self, addr, msg):
        if msg[1] == "JOIN":
            print("-- Received JOIN, adding addr : %s" % addr[0])
            self.nodes.append(addr[0])
            self.sender.simpleMsg(self.sock, addr, "P2P:RJOIN:" + str(len(self.nodes)) + ":" +":".join(str(x) for x in self.nodes))
        
        if msg[1] == "LIST":
            print("-- Receieved LIST, current nodes are : ".join(str(x) for x in self.nodes))
            self.sender.simpleMsg(self.sock, addr, str(self.nodes))
        
        if msg[1] == "RJOIN":
            print("-- Received RJOIN, adding nodes received.")
            for i in range(int(msg[2])):
                print("Adding node: " + str(msg[i+3]))
                self.nodes.append(msg[i+3])
        else:
            pass

class Bucket:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "accountCreds.json"

        self.project_id = "asc23-378811"
        self.bucket_name = "bucketasc"
        
        storage_client = storage.Client()
        self.bucket = storage_client.get_bucket(self.bucket_name)

    # List all objects in the bucket
    def list(self):
        print(f"Objects in bucket {self.bucket_name}:")
        objs = []
        for blob in self.bucket.list_blobs():
            print(f" - {blob.name}")
            objs.append(blob.name)
        return objs

    # Upload a new object to the bucket
    def insert(self, file_path):
        blob_name = os.path.basename(file_path)
        blob = self.bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        print(f"File {file_path} uploaded to {self.bucket_name} as {blob_name}.")

    # Download an object from the bucket
    def get(self, blob_name, destination_path):
        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(destination_path)
        print(f"File {blob_name} downloaded from {self.bucket_name} to {destination_path}.")

    # Delete an object from the bucket
    def delete(self, blob_name):
        blob = self.bucket.blob(blob_name)
        blob.delete()
        print(f"File {blob_name} deleted from {self.bucket_name}.")


class Node:
    def __init__(self, ip, btip):

        #only works inside gcloud VM (metadata)
        #self.externalip = self.get_extip()
        #self.region = self.get_region()

        self.nodeID = str(uuid.uuid4())[:9]
        self.IP = self.get_ip();
        #for local test
        self.IP = ip
        self.PORT = 8080
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.IP, self.PORT))
        self.isBootstrap = True
        self.bootstrapIp = ""
        self.sender = Sender()
        if (btip != "0"):
            self.bootstrapIp = btip
            self.doJoin()
        else:
            self.openListener()
        


    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    # Get node external IP from gcloud metadata
    def get_extip(self):
        url = "http://metadata/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip"
        headers = {"Metadata-Flavor" : "Google"}
        response = requests.get(url, headers=headers)

        ##todo if status code good   
        return response.json
    
    # Get node region from gcloud metadata
    def get_region(self):
        url = "http://metadata.google.internal/computeMetadata/v1/instance/zone"
        headers = {"Metadata-Flavor" : "Google"}
        response = requests.get(url, headers=headers)

        ##todo if status code good   
        return response.json
    
    # Open listening port
    def openListener(self):
        listen = Listener(self)

    def doJoin(self):
        self.openListener()
        self.sender.simpleMsg(self.sock, (self.bootstrapIp, self.PORT), "P2P:JOIN")

if __name__ == "__main__":
    #TODO make sure its an IP
    #Give a bootstrap node or 0 if its a bootstrap node
    if len(sys.argv)>1:
        node = Node(sys.argv[2], sys.argv[1])
    else:
        print("Wrong usage. ex: python3 node.py (bootstrap node IP)")
