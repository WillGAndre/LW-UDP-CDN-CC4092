import os
import socket
import secrets
from logging.config import dictConfig
from pymemcache.client import base
from clientListener import Listener

from flask import Flask, render_template, request, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename

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
app = Flask(__name__)
secret_key = secrets.token_hex(32)
app.secret_key = secret_key
cl_listener = Listener(9000, 1024, app.logger)
cl_listener.listen()

# Example list of content that can be pushed/pulled
content = []

# Set the upload folder and allowed extensions for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

## Basic Cache example ---
client = base.Client(('memcached', 11211))
client.set('token', '123')
# ---

# @app.route("/")
# def home():
#     # Display message
#     html = f"<center><h3>Flask-NGINX-LD-TEST-TOKEN-{client.get('token')}</h3></center>"
#     return html.format(hostname=socket.gethostname())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    if username == "client" and password == "password":
        session['username'] = username
        return render_template("client.html", content=content)
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

    content.append(new_content)

    return render_template("master.html", content=content, success="Content added successfully")


@app.route("/view")
def view():
    return render_template("view.html", content=content)


@app.route('/uploads/<filename>')
def download_file(filename):
    filename = filename.replace(" ", "_")
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)


@app.route('/view/<filename>')
def view_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(file_path, 'r') as f:
        file_contents = f.read()
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

if __name__ == '__main__':
    app.run(host="0.0.0.0")
