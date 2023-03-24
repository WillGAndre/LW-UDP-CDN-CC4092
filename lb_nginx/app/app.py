import socket
from flask import Flask
from pymemcache.client import base

app = Flask(__name__)
client = base.Client(('memcached', 11211))
client.set('token', '123')

# Jinja2
# Route for the default page
@app.route("/")
def home():
    # Display message
    html = f"<center><h3>Flask-NGINX-LD-TEST-TOKEN-{client.get('token')}</h3></center>"
    return html.format(hostname=socket.gethostname())

if __name__ == '__main__':
    app.run(host="0.0.0.0")
