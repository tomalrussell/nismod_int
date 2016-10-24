"""Web frontend - flask app
"""
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, make_response, render_template, safe_join
import json
import os
import psycopg2
import psycopg2.extras
import sys
# todo: fix absolute/relative import (from app.node should work?)
from node import Node

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

@app.route("/nodes")
def nodes_page():
    """List nodes
    """
    conn = psycopg2.connect("dbname=vagrant user=vagrant")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = """SELECT
        ST_X(location::geometry) as lon,
        ST_Y(location::geometry) as lat,
        node_id,
        node_name,
        type,
        status
    FROM sos_i_nodes"""

    # todo: include search/filter form, GET variables
    cur.execute(sql)

    nodes = [Node(f) for f in cur]
    return render_template("node_list.html", nodes=nodes)

@app.route("/nodes/<node_id>")
def node_page(node_id):
    """Node details
    """
    conn = psycopg2.connect("dbname=vagrant user=vagrant")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = """SELECT
        ST_X(location::geometry) as lon,
        ST_Y(location::geometry) as lat,
        node_id,
        node_name,
        type,
        status
    FROM sos_i_nodes
    WHERE node_id = %s"""

    cur.execute(sql, (node_id, ))

    # todo: 404 if rowcount != 1
    data = cur.fetchone()
    node = Node(data)
    return render_template("node_single.html", node=node)


@app.route("/areas")
def areas_page():
    """List available areas
    """
    # todo: create table, select
    areas = ["gaza", "uk"]
    return render_template("area_list.html", areas=areas)

@app.route("/areas/<area_name>")
def area_page(area_name):
    """Area details
    """
    return render_template("area_single.html", area=area_name)

@app.route("/data/<area_name>")
def serve_data(area_name):
    """Serve json data from postgres
    """
    # todo: push getting nodes down into app.node
    # utility method to get NodeCollection.asJSON()
    conn = psycopg2.connect("dbname=vagrant user=vagrant")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    sql = """SELECT
        ST_AsGeoJSON(location)::json as geometry,
        node_id,
        node_name,
        type
    FROM sos_i_nodes
    WHERE area = %s"""

    cur.execute(sql, (area_name, ))

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
