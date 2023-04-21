import requests
import os;
import socket;

KEY = "AIzaSyCQ65jgh0Xzkdg2u-ev5TZJz7CtUlqghYo"
BUCKETNAME ="bucketasc"
ACCOUNTCREDS = "accountCreds.json"


class Node:
    def __init__(self):
        self.externalip = self.get_extip()
        self.region = self.get_region()
        self.port = self.getport()

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
    