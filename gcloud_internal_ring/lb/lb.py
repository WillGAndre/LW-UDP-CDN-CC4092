import socket
import os
import sys
import time
import threading
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename

lbZone = sys.argv[1]
lbRemoteNode = ["10.128.0.4"]
lbNodePort = 4444
lbBuckets = []
lbContent = []
# lbArrivals = []
lbUploadsDir = '/tmp/'
lbArrivalsDir = '/tmp/'
app = Flask(__name__)
secret_key = secrets.token_hex(32)
app.secret_key = secret_key
app.config['UPLOAD_FOLDER'] = lbUploadsDir

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
            lbBuckets.insert(0, message.split(';')[0].split(':')[1])
            lbRemoteNode.insert(0, message.split(';')[1].split(':')[1])
        elif "res-insert" in message:
            msplit = message.split(':')
            filename = msplit[1]
            filedata = "saved to bucket"
            with open(f"{lbArrivalsDir}arr-{filename}", "w") as file:
                file.write(filedata)
            print(f"Saved bucket file to: {lbArrivalsDir}arr-{filename}")

        print(f"Received '{message}' from {address[0]}:{address[1]}")

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    if username == "client" and password == "password":
        session['username'] = username
        return render_template("client.html", content=lbContent)
    elif username == "master" and password == "password":
        session['username'] = username
        return render_template("master.html")
    else:
        return render_template("index.html", error="Invalid credentials")

@app.route("/push", methods=["POST"])
def push():
    # Example push logic for Master user
    new_content = {}
    new_text = request.form.get("text")
    new_text_file = request.files.get("text_file")
    new_image_file = request.files.get("image_file")

    if new_text_file:
        new_content["type"] = "text"
        new_content["filename"] = new_text_file.filename
        new_text_file.save(os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(new_text_file.filename)))
    if new_image_file:
        filename = secure_filename(new_image_file.filename)
        new_image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        new_content["type"] = "image"
        new_content["filename"] = filename

    lbContent.append(new_content)

    return render_template("master.html", content=lbContent, success="Content added successfully")

@app.route("/view")
def view():
    # session['username']
    return render_template("view.html", content=lbContent)


@app.route('/uploads/<filename>')
def download_file(filename):
    filename = filename.replace(" ", "_")
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

@app.route('/view/<filename>')
def view_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(file_path, 'r') as f:
        file_contents = f.read()

    node = lbRemoteNode[0]
    try:
        send_udp_message(f"lb:insert:{filename}", node, lbNodePort)
        with open(file_path, 'rb') as file:
            file_len = os.path.getsize(file_path)
            proc_len = 1024
            chunk = file.read(1024)
            while chunk:
                if proc_len >= file_len:
                    send_udp_message(f"lbfc:{filename}:{chunk}", node, lbNodePort)           # UDP limitation
                else:
                    send_udp_message(f"lbc:{filename}:{chunk}", node, lbNodePort)
                chunk = file.read(1024)
                proc_len += 1024
        print(f'File "{file_path}" sent successfully')
    except Exception as e:
        pass
    time.sleep(5)
    return render_template("view_file.html", filename=filename, file_contents=file_contents)

@app.route('/view_file_content/<string:filename>')
def view_file_content(filename):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    with open(filepath, 'r') as file:
        content = file.read()
    return render_template('view_file_content.html', content=content)


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/stats')
def stats():
    return f"LB Zone: {lbZone} \nRemote Nodes: {lbRemoteNode} \nBucket Refs: {lbBuckets} \nArrivals: {os.listdir(lbArrivalsDir)}"

@app.route('/insert')
def insert():
    file_path = f"{lbUploadsDir}text3.txt"
    node = lbRemoteNode[0]
    try:
        send_udp_message(f"lb:insert:text3.txt", node, lbNodePort)                          # ******
        with open(file_path, 'rb') as file:
            file_len = os.path.getsize(file_path)
            proc_len = 1024
            chunk = file.read(1024)
            while chunk:
                if proc_len >= file_len:
                    send_udp_message(f"lbfc:text3.txt:{chunk}", node, lbNodePort)           # UDP limitation
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
            print(f"waiting for arrival... | Arrival check: {os.path.exists(f'{lbArrivalsDir}arr-text3.txt')}")
            input()

    return f"""
        Pushed {file_path} to remote bucket \n\n\n\n
        {file_contents}
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

# if __name__ == "__main__":
#     insert_thread = threading.Thread(target=insert)
#     insert_thread.start()
#     debug_thread = threading.Thread(target=debug)
#     debug_thread.start()
#     insert_thread.join()
#     debug_thread.join()
