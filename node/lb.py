import socket
import os

def insert():
    own_addr = ("192.168.1.137", 4445)
    node_addr = ("10.128.0.4", 4445)
    size = 1024
    encoding = "utf-8"
    filename = "text3.txt"
    fileWDir = "files/"+filename


    """ Creating a TCP socket """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(own_addr)
    server.listen()
    print("[+] Listening...")
 
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((own_addr[0], 4444))
    udp.sendto(("insert:"+filename +"\n").encode(), (node_addr[0], 4444))

    
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




def get():
    own_addr = ("127.0.0.2", 8081)
    node_addr = ("127.0.0.1", 8081)
    ADDR = ("127.0.0.2", 8081)
    size = 1024
    encoding = "utf-8"
    filename = "cloud.png"


    """ Creating a TCP server socket """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(own_addr)
    server.listen()
    print("[+] Listening...")
 
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind((own_addr[0], 8080))
    udp.sendto(("get:"+ filename +"\n").encode(), (node_addr[0], 8080))

    
    """ Accepting the connection from the client. """
    conn, addr = server.accept()
    print(f"[+] Client connected from {addr[0]}:{addr[1]}")
 
    """ Receiving the filename and filesize from the client. """
    data = conn.recv(size).decode(encoding)
    item = data.split("_")
    FILENAME = item[0]
    if FILENAME != filename:
        print("Something went wrong, different filenames")
    FILESIZE = int(item[1])
 
    print("[+] Filename and filesize received from the client.")
    conn.sendall("Filename and filesize received".encode(encoding))
 
    """ Data transfer """

    with open(f"Received/recv_{FILENAME}", "wb") as f:
        while True:
            data = conn.recv(size)
 
            if not data:
                break
 
            f.write(data)
            conn.sendall("Data received.".encode(encoding))
 
            
    """ Closing connection. """
    conn.close()
    server.close()
 
if __name__ == "__main__":
    insert()