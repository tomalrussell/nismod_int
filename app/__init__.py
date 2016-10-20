"""Web frontend - flask app
"""
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, make_response, render_template, safe_join
import json
import os
import psycopg2
import psycopg2.extras
import sys

# load environment variables
load_dotenv(find_dotenv())

PY3 = (sys.version_info[0] == 3)
DEBUG = (os.environ.get("DEBUG") == "true")
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
DATA_DIR = os.path.join(SITE_ROOT, "data")

app = Flask(__name__)
app.debug = DEBUG

@app.route("/")
def hello():
    """Render index.html page at site root
    """
    return render_template("index.html")

@app.route("/data/<area_name>")
def serve_data(area_name):
    """Serve json data from postgres
    """
    conn = psycopg2.connect("dbname=vagrant user=vagrant")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = """SELECT
        ST_AsGeoJSON(location)::json as geometry,
        node_id,
        node_name,
        type
    FROM sos_i_nodes"""

    cur.execute(sql)

    features = [{
        "type": "Feature",
        "geometry": f["geometry"],
        "properties": {
            "id": f["node_id"],
            "name": f["node_name"],
            "type": f["type"]
        }
    } for f in cur]
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    resp = make_response(json.dumps(geojson), 200)
    resp.headers['Content-Type'] = "application/json"
    return resp

if __name__ == "__main__":
    app.run(port=5050)
