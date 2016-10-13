"""Web frontend - flask app
"""
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, make_response, render_template
import os

load_dotenv(find_dotenv())

DEBUG = (os.environ.get("DEBUG") == "true")

app = Flask(__name__)
app.debug = DEBUG

@app.route("/")
def hello():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=5050)
