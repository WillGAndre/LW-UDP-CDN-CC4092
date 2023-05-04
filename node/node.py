import requests
import os
import socket
import nodeListener



class Node:
    def __init__(self):
        #self.externalip = self.get_extip()
        #self.region = self.get_region()
        #self.port = self.getport()
        self.node = ""
        

    def get_port(self):
        os.environ.get('PORT', 8080)

    def get_extip(self):
        url = "http://metadata/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip"
        headers = {"Metadata-Flavor" : "Google"}

        response = requests.get(url, headers=headers)

        ##todo if status code good   
        return response.json
    
    def get_region(self):
        url = "http://metadata.google.internal/computeMetadata/v1/instance/zone"
        headers = {"Metadata-Flavor" : "Google"}

        response = requests.get(url, headers=headers)
        ##todo if status code good   
        return response.json
    
    def openListener(self):
        listen = nodeListener.Listener()

if __name__ == "__main__":

    node = Node()
    node.openListener()
