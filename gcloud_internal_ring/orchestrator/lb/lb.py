import socket
import os
import sys
import time
import threading
from flask import Flask

lbZone = sys.argv[1]
lbRemoteNode = ["10.128.0.4"]
lbNodePort = 4444
lbBuckets = []
lbArrivals = []
lbUploadsDir = '/tmp/'
lbArrivalsDir = '/tmp/'
app = Flask(__name__)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def send_udp_message(message, host, port, encode=True):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if encode:
        sock.sendto(message.encode(), (host, port))
    else:
        sock.sendto(message, (host, port))
    print(f"Sent UDP message: {message}")

def receive_udp_message(port):
    global lbRemoteNode, lbBuckets
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
    print(f"Listening for UDP messages on port {port}")

    while True:
        data, address = sock.recvfrom(1024)
        message = data.decode()
        if message == "JOIN":
            # lbRemoteNode.append(address[0])
            lbRemoteNode.insert(0, address[0])
        elif "bucket" in message:
            lbBuckets.append(message.split(';')[0].split(':')[1])
        elif "res-insert" in message:
            msplit = message.split(':')
            filename = msplit[1]
            filedata = "saved to bucket"
            with open(f"{lbArrivalsDir}arr-{filename}", "w") as file:
                file.write(filedata)
            print(f"Saved bucket file to: {lbArrivalsDir}arr-{filename}")

        print(f"Received '{message}' from {address[0]}:{address[1]}")

@app.route('/')
def hello():
    return 'Hello, Flask on GCP!'

@app.route('/stats')
def stats():
    return f"LB Zone: {lbZone} \nRemote Nodes: {lbRemoteNode} \nBucket Refs: {lbBuckets}"

@app.route('/insert')
def insert():
    file_path = f"{lbUploadsDir}text3.txt"
    node = lbRemoteNode[0]
    try:
        send_udp_message(f"lb:insert:text3.txt", node, lbNodePort)                         # ******
        with open(file_path, 'rb') as file:
            file_len = os.path.getsize(file_path)
            proc_len = 1024
            chunk = file.read(1024)
            while chunk:
                if proc_len >= file_len:
                    send_udp_message(f"lbfc:text3.txt:{chunk}", node, lbNodePort)
                else:
                    send_udp_message(f"lbc:text3.txt:{chunk}", node, lbNodePort)
                chunk = file.read(1024)
                proc_len += 1024
        print(f'File "{file_path}" sent successfully')
    except Exception as e:
        print(f'Error occurred while sending file: {str(e)}')
    time.sleep(5)

    file_contents = None
    while file_contents == None:
        if os.path.exists(f"{lbArrivalsDir}arr-text3.txt"):
            with open(f"{lbArrivalsDir}arr-text3.txt", 'r') as file:
                file_contents = file.read()

        if file_contents == None:
            # send_udp_message(f"lb:insert:text3.txt:", lbRemoteNode[0], lbNodePort)
            print(f"waiting for arrival... | Does the file exist: {os.path.exists(f'{lbArrivalsDir}arr-text3.txt')}")
            input()

    return f"""
        Pushed {file_path} to remote bucket\n
        
        Lorem ipsum dolor sit amet\n

        Arrival: \nFile contents >> {file_contents}
    """

if __name__ == '__main__':
    send_udp_message("JOIN", lbRemoteNode[0], lbNodePort)
    time.sleep(5)
    receive_thread = threading.Thread(target=receive_udp_message, args=(lbNodePort,))
    receive_thread.start()
    while not len(lbBuckets):
        send_udp_message(f"lb:getbucket:{lbZone}", lbRemoteNode[0], lbNodePort)
        time.sleep(7)
    app.run(host='0.0.0.0', port=5000)
    receive_thread.join()

def insert():
    own_addr = (get_ip(), 4445)
    node_addr = ("10.128.0.4", 4445)
    size = 1024
    encoding = "utf-8"
    filename = "text3.txt"
    fileWDir = filename


    """ Creating a TCP socket """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(own_addr)
    server.listen()
    print("[+] Listening...")
 
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((own_addr[0], lbNodePort))
    udp.sendto(("lb:insert\n").encode(), (node_addr[0], lbNodePort))

    
    """ Accepting the connection from the client. """
    conn, addr = server.accept()
    print(f"[+] Client connected from {addr[0]}:{addr[1]}")
    conn.recv(size).decode(encoding)

    """ Sending the filename and filesize to the server. """
    file_size = os.path.getsize(fileWDir)
    data = f"{filename}_{file_size}"
    conn.sendall(data.encode(encoding))
    msg = conn.recv(size).decode(encoding)
    print(f"SERVER: {msg}")
    
    """ Data transfer. """
    with open(fileWDir, "rb") as f:
        while True:
            data = f.read(size)
            if not data:
                break
    
            conn.sendall(data)
            msg = conn.recv(size).decode(encoding)

    """ Closing the connection """
    conn.close()

def debug():
    while True:
        time.sleep(5)
        input()

# if __name__ == "__main__":
#     insert_thread = threading.Thread(target=insert)
#     insert_thread.start()
#     debug_thread = threading.Thread(target=debug)
#     debug_thread.start()
#     insert_thread.join()
#     debug_thread.join()
