"""Web frontend - flask app
"""
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, make_response, render_template, safe_join
import json
import os

load_dotenv(find_dotenv())

DEBUG = (os.environ.get("DEBUG") == "true")
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
DATA_DIR = os.path.join(SITE_ROOT, "data")

app = Flask(__name__)
app.debug = DEBUG

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/data/<filename>")
def serve_static_data(filename):
    path = safe_join(DATA_DIR, filename)
    if not os.path.exists(path):
        data = '{"error": "Not found"}'
        code = 404
    else:
        with open(path, 'r', encoding='utf-8') as file_handle:
            data = file_handle.read()
        code = 200

    resp = make_response(data, code)
    resp.headers['Content-Type'] = "application/json"
    return resp

if __name__ == "__main__":
    app.run(port=5050)
