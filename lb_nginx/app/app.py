import socket
from logging.config import dictConfig
from flask import Flask
from pymemcache.client import base
from clientListener import Listener

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
cl_listener = Listener(9000, 1024, app.logger)
cl_listener.listen()

## Basic Cache example ---
client = base.Client(('memcached', 11211))
client.set('token', '123')
# ---

# Jinja2
# Route for the default page
@app.route("/")
def home():
    # Display message
    html = f"<center><h3>Flask-NGINX-LD-TEST-TOKEN-{client.get('token')}</h3></center>"
    return html.format(hostname=socket.gethostname())

if __name__ == '__main__':
    app.run(host="0.0.0.0")
