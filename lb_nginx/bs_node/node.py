import requests
import sys
import socket
import os
import threading
from google.cloud import storage
import uuid
import logging
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

class Node:
    def __init__(self, ip, btip):

        #only works inside gcloud VM (metadata)
        #self.externalip = self.get_extip()
        #self.region = self.get_region()

        self.nodeID = str(uuid.uuid4())[:9]
        self.IP = self.get_ip()
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
        logging.info("Node listening on port %s" %self.node.PORT)
        
        while True:
            data, addr = self.sock.recvfrom(1024)
            thread = threading.Thread(target=self.handler, args=(data, addr))
            thread.start()

    # Handle data recieved
    def handler(self, data, addr):
        logging.info("recieved : %s from %s" % (data , addr))

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
            filename = msg[1]
            rq = bucket.delete(filename)
            sender.simpleMsg(self.sock, addr, "200")
        elif (msg[0] == "insert"):
            filename = msg[1]
            sender.upload_fromName(addr, filename)
        elif (msg[0] == "get"):
            filename = msg[1]
            sender.sendFile_fromName(addr, filename)
            #P2P messages
        elif (msg[0] == "P2P"):
            self.ptp.handle(addr, msg)

    
class Sender:
    def simpleMsg(self, sock, addr, msg):
        logging.info("sending : " + str(msg) +" to " + addr[0] +":" + str(addr[1]))
        
        sock.sendto((msg +"\n").encode(), addr)

    def upload_fromName(self, addr, filename):
        addr = (addr[0], 8081)
        size = 1024
        encoding = "utf-8"


        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(addr)
        client.send("READY".encode(encoding))

        """ Receiving the filename and filesize from the client. """
        data = client.recv(size).decode(encoding)
        item = data.split("_")
        if filename != item[0]:
            logging.info("Something went wrong. Filename not the same")
        file_size = int(item[1])
 
        logging.info("[+] Filename and filesize received from the client.")
        client.sendall("Filename and filesize received".encode(encoding))

        with open(f"files/recv_{filename}", "wb") as f:
            while True:
                data = client.recv(size)
    
                if not data:
                    break
    
                f.write(data)
                client.sendall("Data received.".encode(encoding))

        client.close()

        #file uploaded to local, now uploading to gcloud
        bucket = Bucket()
        bucket.insert("files/recv_"+filename, filename)

    def sendFile_fromName(self, addr, filename):
        encoding = "utf-8"
        size = 1024
        fileWDir = "files/"+filename
        bucket = Bucket()
        logging.info("Downloading file from bucket")

        bucket.get(filename, fileWDir)
        file_size = os.path.getsize(fileWDir)

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((addr[0], 8081))

        """ Sending the filename and filesize to the server. """
        data = f"{filename}_{file_size}"
        client.sendall(data.encode(encoding))
        msg = client.recv(size).decode(encoding)
        logging.info(f"SERVER: {msg}")
    
        """ Data transfer. """
        logging.info(fileWDir)
        with open(fileWDir, "rb") as f:
            logging.info(f.name)
            logging.info("loop")
            while True:
                data = f.read(size)
                logging.info(data)
                if not data:
                    break
    
                client.sendall(data)
                msg = client.recv(size).decode(encoding)

        """ Closing the connection """
        client.close()
 

class Ptp:
    def __init__(self, socket):
        self.nodes = []
        self.buckets = []
        self.sock = socket
        self.sender = Sender()

    #send PING to network
    def ping(self):
        for node in self.nodes:
            self.sender.simpleMsg(self.sock, node, "PING")    

    # Add bucket id/creds to list
    def handle(self, addr, msg):
        if msg[1] == "JOIN":
            logging.info("-- Received JOIN, adding addr : %s" % addr[0])
            self.sender.simpleMsg(self.sock, addr, "P2P:RJOIN:" + str(len(self.nodes)) + ":" +":".join(str(x) for x in self.nodes))
            self.nodes.append(addr[0])
        
        if msg[1] == "LIST":
            logging.info("-- Receieved LIST, current nodes are : ".join(str(x) for x in self.nodes))
            self.sender.simpleMsg(self.sock, addr, str(self.nodes))
        
        if msg[1] == "RJOIN":
            logging.info("-- Received RJOIN, adding and sending JOIN to nodes received.")
            for i in range(int(msg[2])):
                if msg[i+3] not in self.nodes:
                    logging.info("Adding node: " + str(msg[i+3]))
                    self.nodes.append(msg[i+3])
                    self.sender.simpleMsg(self.sock, (msg[i+3], 8080), "P2P:JOIN")
        else:
            pass

class Bucket:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "accountCreds.json"

        self.project_id = "asc23-378811"
        self.bucket_name = "bucketasc"  
        
        storage_client = storage.Client()
        self.bucket = storage_client.get_bucket(self.bucket_name)

    # TODO: Create Bucket

    # List all objects in the bucket
    def list(self):
        logging.info(f"Objects in bucket {self.bucket_name}:")
        objs = []
        for blob in self.bucket.list_blobs():
            logging.info(f" - {blob.name}")
            objs.append(blob.name)
        return objs

    # Upload a new object to the bucket
    def insert(self, file_path, filename):
        blob_name = filename
        blob = self.bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        logging.info(f"File {file_path} uploaded to {self.bucket_name} as {blob_name}.")

    # Download an object from the bucket
    def get(self, blob_name, destination_path):
        blob = self.bucket.blob(blob_name)
        blob.download_to_filename(destination_path)
        logging.info(f"File {blob_name} downloaded from {self.bucket_name} to {destination_path}.")

    # Delete an object from the bucket
    def delete(self, blob_name):
        blob = self.bucket.blob(blob_name)
        blob.delete()
        logging.info(f"File {blob_name} deleted from {self.bucket_name}.")

if __name__ == "__main__":
    #TODO make sure its an IP
    #Give a bootstrap node or 0 if its a bootstrap node
    if len(sys.argv)>1:
        node = Node(sys.argv[2], sys.argv[1])
    else:
        logging.info("Wrong usage. ex: python3 node.py (bootstrap node IP)")
