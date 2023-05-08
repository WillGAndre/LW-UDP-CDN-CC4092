import requests
import nodeListener
import sys



class Node:
    def __init__(self):

        #only works inside gcloud VM (metadata)
        #self.externalip = self.get_extip()
        #self.region = self.get_region()
        self.nodeID = ""


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
    
    # Open listening port
    def openListener(self):
        listen = nodeListener.Listener()

if __name__ == "__main__":
    #TODO make sure its an IP
    if len(sys.argv)>1:
        print(sys.argv[1])
    node = Node()
    node.openListener()
