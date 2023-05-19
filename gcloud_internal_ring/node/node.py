GCLOUD_CREDS = "asc23-378811-ca4948da7594.json"

import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def homepage():
    if request.method == "GET":
        return jsonify({"message": "Hello World!"})

PORT = int(os.environ.get("PORT", 8080))
if __name__ == '__main__':
    print("starting internal node...")
    app.run(threaded=True,host='0.0.0.0',port=PORT)
