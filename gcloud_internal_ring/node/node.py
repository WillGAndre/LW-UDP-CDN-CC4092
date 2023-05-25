import os
import sys
import ssl
import json
import uuid
import time
import socket
import threading
import subprocess

from google.cloud import storage
from google.oauth2 import service_account

credentials = """
{
  "type": "service_account",
  "project_id": "asc23-378811",
  "private_key_id": "ca4948da759426e5d3729a968ed62cc2ecb19d44",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDuyUsprPirmj5Y\\nb4tSTzRXJpNTnLajjgEd/ZnmD6GYbnWjlejBVaeA+oE3Lthb9pgSNmFkhgGScJDy\\n1ybCWnfWig8uiVCsJD8iWrh2m9ttYZOi9vyGWYMmoGJ2ownAQhS6QtFlg2BVuYGA\\nxP17V6emnUJWDS2/1bPI4AtB5znkmn6aHX8uUiE8QTGZfjetig/PnojiG8vG4WUG\\nHkmIHr0s4f6DbOsfpjw2RHKqHjsJ1OFHerbub3QHJzzdaYOBQ0N2hn0vbK4PEmmH\\negAduA/uEaLAFkFpQCdocwoyiej+9GW7NpwrXP+BFcCaVG0KiVNBla6IQAxMzUMT\\nF4OFRh0HAgMBAAECggEACHRvKWAbA/R3rajxbW4pg8Z1Y/oCC4N9LaMrnlZCWgPb\\nPXoS3jmarznvdlU9yu/NzaNISodmKdm7gCW3FR2f7aRAylyJUzcLVzuQGX8GQ3a3\\nhAcrxNQJjUYThnDaaQjN9BRmlqoSsKZbXARdl07wvDkIPsTDsG2wKnYoX+KAjcQL\\nIcH69ZLizzcPPrIUueWn4rVw1/lzaF5Kb3Xrmm6PnBFKPQOO9Mw7Sm2IDhTSRIvD\\nOt3Hp1oJEHjju2F9497vE1GqC0iQW9Pcwsien5L387CVPC0MfW7ciQMjzk8u7f1t\\nIpqOAFX8FNF90BY1Az7YbyzkFM/0yhJ5l6gNqZWXEQKBgQD7DhZzt76vK1nuqF6k\\nhHYoOq8hMPN650aSGQtom57i8AfRTn5uUpveh8dIACuoD9adrNlvEubX38ErhjGH\\nHHNScBo1tcA8KUWE2mIFPVdsonRoLp8lT0aRh0KUAF8GWdhNrWzc0OLfaJXBl3PH\\nJSuGBAIZ+Ts+a5RFV6fKEN5cMQKBgQDzfVeqX+wL16lD9jeiKqKg/cJjZhtPn+15\\n3ob8BiGF/k+wnurZpudiaGZG5MMnGOE4Hcz3MsbXHqIdcjkBCt1oFrlagu29Qke5\\n2wAbEaAuD9D6RxPbkM6ecYZr/zNMbHnMQo5F2MvTxnffgYYeXy0veqiRcn8jmJoq\\nc+6rNUYWtwKBgCP/WB7NiOzrBWEgCToDuEF6cKQMtcy4nrjSGH2uWrDlg+lyHNTK\\nyYi15VAgniHh637+SssPZcQsVDFec3mRDcQTSN7Mqby2mj47ZfSkYAW2oYRSswUR\\ngefaAiTgjL+HYGl65XIgDXfFMjvo8HPsk3oK1xZMUz9XA5KRyABEPO3xAoGBALRb\\nA7SPmKis9hQBLPRR4GSfkn1OBKzWKXE8A4BqiipWVXDeRdcyafHaouegS22KYEjQ\\nyiHQ2rg9WJe3I8JB6f5P1rvUf4TQs5BXR5zFUYDM9l5sh6j7ehCixo74WWcicpV6\\nNyhFjbUwLVrA9jdJCI9Cq9oQlVwojQklFoR60Y/BAoGBAOLwcKOPgkw+Dmfl8F97\\nC+sK4ybJsGq8ip+sa7BM43pklpECQrKIKz+i7gRFPUpdX0pV0kqUrwN7FsO1ro5O\\ngBQmiz+MEh307rg6mwr6+C692c5360DP7QtoPuG2Y+wzPXyF2ezAQ8sn+c3laucg\\nA1dauAaNZy2/H/fNTrITIC+b\\n-----END PRIVATE KEY-----\\n",
  "client_email": "csa-internal-ring@asc23-378811.iam.gserviceaccount.com",
  "client_id": "115178825426682928049",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/csa-internal-ring&#37;40asc23-378811.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
""" # Env Var

# Create a temporary credentials file
credentials_file = "credentials.json"
with open(credentials_file, "w") as f:
    f.write(credentials)

# Authenticate with Google Cloud using the temporary credentials file
credentials = service_account.Credentials.from_service_account_file(credentials_file)
storage_client = storage.Client(credentials=credentials)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_file

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def send_udp_message(message, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (host, port))
    print(f"Sent UDP message: {message}")

def receive_udp_message(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
    print(f"Listening for UDP messages on port {port}")

    while True:
        data, address = sock.recvfrom(1024)
        message = data.decode()

        if message == "JOIN":
            if address[0] not in nodes:
                nodes.append(address[0])
                for nodeaddr in nodes:
                    send_udp_message(f"ADD:{address[0]}", nodeaddr, nodePort)
                send_udp_message("JOIN", address[0], nodePort)
        elif "ADD:" in message:
            nodeaddr = message.split(':')[1]
            if nodeaddr not in nodes:
                nodes.append(nodeaddr)
            send_udp_message("JOIN", nodeaddr, nodePort)
        elif "BQUERY:" in message:
            msg_split = message.split(':')
            target = msg_split[1]
            location = msg_split[2] # Location Type: Zone
            if location == nodeZone:
                send_udp_message(f"bucket:{bucket_name};node:{nodeHost}", target, nodePort)
        elif "BINSERT:" in message:
            msg_split = message.split(':')
            file = msg_split[1]
            json_object = [
                {
                    "filename": file,
                    "maintainer": address[0]
                }
            ]
            push_json_objects(bucket_name, json_object, f"ref-{file}")
            retrieved_json_objects = get_json_objects(bucket_name, f"ref-{file}")
            print(f"Created {file} with {retrieved_json_objects}")
        elif "lb:list" in message:
            if address[0] not in external_nodes:
                external_nodes.append(address[0])
            print(f"Objects in bucket {bucket_name}:")
            bucket = storage_client.bucket(bucket_name)
            objs = []
            for blob in bucket.list_blobs():
                print(f" - {blob.name}")
                objs.append(blob.name)
            send_udp_message(f"list:{objs}", address[0], nodePort)
        elif "lb:getbucket" in message:
            if address[0] not in external_nodes:
                external_nodes.append(address[0])
            send_udp_message(f"bucket:{bucket_name};node:{nodeHost}", address[0], nodePort)
            location = message.split(':')[2]
            for nodeaddr in nodes:
                send_udp_message(f"BQUERY:{address[0]}:{location}", nodeaddr, nodePort)
        elif "lb:insert" in message: # lb:insert:<filename>
            if address[0] not in external_nodes:
                external_nodes.append(address[0])
            msplit = message.split(':')

            filename = msplit[2]
            nodeFiles[filename] = b''
            for nodeaddr in nodes:
                send_udp_message(f"BINSERT:{filename}", nodeaddr, nodePort)
        elif "lbc" in message:
            if address[0] not in external_nodes:
                external_nodes.append(address[0])
            msplit = message.split(':')

            filename = msplit[1]
            chunk = msplit[2]
            if filename in nodeFiles:
                nodeFiles[filename] += chunk.encode()
            else:
                nodeFiles[filename] = chunk.encode()
        elif "lbfc" in message:
            if address[0] not in external_nodes:
                external_nodes.append(address[0])
            msplit = message.split(':')

            filename = msplit[1]
            chunk = msplit[2]
            if filename in nodeFiles:
                nodeFiles[filename] += chunk.encode()
            else:
                nodeFiles[filename] = chunk.encode()

            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_string(nodeFiles[filename])

            res_file_data = get_file_objects(bucket_name, filename)
            print(f"Added {filename} to bucket: {res_file_data}")
            for nodeaddr in nodes:
                send_udp_message(f"res-insert:{filename}", nodeaddr, nodePort)
            send_udp_message(f"res-insert:{filename}", address[0], nodePort)

        print(f"Received '{message}' from {address[0]}:{address[1]} \n Nodes={nodes} Buckets={buckets}")

def debug():
    while True:
        print(f"Nodes: {nodes} External Nodes: {external_nodes} Buckets: {buckets} Node Files: {nodeFiles}")
        input()
        # command = input("Enter a command to send: ")
        # send_udp_message(command, get_ip(), 4444)

def check_bucket(bucket_name) -> bool:
    return storage_client.bucket(bucket_name).exists()

def create_bucket(bucket_name, location):
    # Create the bucket using the Storage client
    bucket = storage_client.create_bucket(bucket_name, location=location)
    print(f"Bucket '{bucket_name}' created successfully.")

def push_json_objects(bucket_name, json_objects, remote_file):
    # Serialize the list of JSON objects
    json_data = json.dumps(json_objects)

    # Push JSON objects to the bucket
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(remote_file)
    blob.upload_from_string(json_data, content_type="application/json")
    print(f"JSON objects pushed to '{remote_file}' successfully.")

def get_json_objects(bucket_name, remote_file):
    # Get JSON objects from the bucket
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(remote_file)
    json_data = blob.download_as_text()

    # Deserialize the JSON objects
    json_objects = json.loads(json_data)
    return json_objects

def get_file_objects(bucket_name, remote_file):
    # Get file objects from the bucket
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(remote_file)
    file_data = blob.download_as_text()

    return file_data

if __name__ == "__main__":

    nodePort = 4444
    nodeID = uuid.uuid4()
    nodeZone = sys.argv[1]
    nodeType = sys.argv[2]  # 0 --> orchestrator | 1 --> internal | 2 --> external
    nodeHost = f"{get_ip()}:{nodePort}"
    nodeCertFile = "node.crt"
    nodeKeyFile = "node.key"
    nodeFiles = {}

    nodes          = []
    external_nodes = []
    buckets        = []

    zone_split = nodeZone.split('-')
    print(f"node init - {nodeHost}")

    bucket_name = f"internal-ring-bucket-{nodeID}"
    nodeLocation = f"{zone_split[0]}-{zone_split[1]}"  # Choose your desired location
    json_objects = [
        {
            "maintainer-id": nodeHost,
            "zone": nodeZone
        }
    ]
    remote_file = "init.json"

    if not check_bucket(bucket_name):
        create_bucket(bucket_name, nodeLocation)
        push_json_objects(bucket_name, json_objects, remote_file)
        retrieved_json_objects = get_json_objects(bucket_name, remote_file)
        print(retrieved_json_objects)
    else:
        print(f"Bucket '{bucket_name}' already exists.")
    buckets.append((bucket_name, nodeZone))

    if nodeType != "0":
        send_udp_message("JOIN", "10.128.0.4", 4444)

    print("SET 1/1")

    receive_thread = threading.Thread(target=receive_udp_message, args=(nodePort,))
    receive_thread.start()

    debug_thread = threading.Thread(target=debug)
    debug_thread.start()

    receive_thread.join()
    debug_thread.join()

    # Clean up the temporary credentials file
    subprocess.run(["rm", credentials_file])
