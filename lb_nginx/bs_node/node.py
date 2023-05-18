import os
import uuid
import socket
import requests
import logging
from logging.config import dictConfig
from google.cloud import storage

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
    def __init__(self, nodeID):
        #only works inside gcloud VM (metadata)
        #self.externalip = self.get_extip()
        #self.region = self.get_region()
        self.nodeID = nodeID
        self.IP = "0.0.0.0"
        self.PORT = os.environ.get('PORT', 8080)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.IP, self.PORT))

        logging.info(f"✅ Started Node with ID={nodeID}")
        self.listen()

    # Get node external IP from metadata
    def get_extip(self):
        url = "http://metadata/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip"
        headers = {"Metadata-Flavor" : "Google"}
        response = requests.get(url, headers=headers)

        ##todo if status code good   
        return response.json
    
    # Get node region from metadata
    def get_region(self):
        url = "http://metadata.google.internal/computeMetadata/v1/instance/zone"
        headers = {"Metadata-Flavor" : "Google"}
        response = requests.get(url, headers=headers)

        ##todo if status code good   
        return response.json

    # Server listening loop
    def listen(self):
        logging.debug("Node listening on port %s" %self.PORT)
        
        while True:
            data, addr = self.sock.recvfrom(1024)
            self.handler(data, addr)

    # Handle data recieved
    def handler(self, data, addr):
        logging.info("recieved : %s from %s" % (data , addr))

        # Create bucket control to handle commands
        bucket = Bucket()

        #POSSIBLE COMMANDS
        # list insert, get, delete
        # sends success/error message with data
        #TODO return error messages

        msg = data.rstrip().decode('ASCII')
        if (msg == "list"):
            rq = bucket.list()
            self.simpleMsg(self.sock, addr, ("200: %s\n" % rq).encode())

        elif (msg.startswith("delete")):
            #TODO check if filename is actually there
            filename = msg.split(" ")[1]
            rq = bucket.delete(filename)
            self.simpleMsg(self.sock, addr, "200\n".encode())

        elif (msg.startswith("insert")):
            #TODO wait for file to be sent in another message
            self.simpleMsg(self.sock, addr, "ready\n".encode())

        elif (msg.startswith("get")):
            #TODO get actual file and send
            filename = msg.split(" ")[1]
            self.simpleMsg(self.sock, addr, ("getting %s\n" %filename ).encode())
        else:
            self.simpleMsg(self.sock, addr, "Command undefined\n".encode())

    def simpleMsg(self, sock, addr, msg):
        logging.info("sending " + str(msg) +"to " + addr[0] +":" + str(addr[1]))
        sock.sendto(msg, addr)

class Bucket:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "accountCreds.json"

        self.project_id = "asc23-378811"
        self.bucket_name = "bucketasc"
        
        storage_client = storage.Client()
        self.bucket = storage_client.get_bucket(self.bucket_name)

    # List all objects in the bucket
    def list(self):
        logging.info(f"Objects in bucket {self.bucket_name}:")
        objs = []
        for blob in self.bucket.list_blobs():
            logging.info(f" - {blob.name}")
            objs.append(blob.name)
        return objs

    # Upload a new object to the bucket
    def insert(self, file_path):
        blob_name = os.path.basename(file_path)
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
    id = f"BS-{uuid.uuid4()}"
    logging.info(f"🏁 Node {id} initialization...")
    Node(id)

    # bk = Bucket()
    # bk.list()
