import socket
from flask import Flask

app = Flask(__name__)

# Route for the default page
@app.route("/")
def home():
    # Display message
    html = "<center><h3>Flask-NGINX-LD-TEST</h3></center>"
    return html.format(hostname=socket.gethostname())

if __name__ == '__main__':
    app.run(host="0.0.0.0")
