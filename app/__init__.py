"""Web frontend - flask app
"""
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, make_response, render_template, safe_join, abort
import json
import os
import psycopg2
import psycopg2.extras
import sys
# todo: fix absolute/relative import (from app.node should work?)
from node import Node
from node_type import get_node_types

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

@app.errorhandler(404)
def page_not_found(error):
    """Handle not found errors
    Throw a 404 from code with `abort(404)`.
    """
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle internal errors
    When not in debug mode, render a simple error page.
    """
    return render_template('500.html'), 500

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
    try:
        node_id = int(node_id)
    except ValueError:
        abort(404)

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

    if cur.rowcount != 1:
        abort(404)

    data = cur.fetchone()
    node = Node(data)
    node_types = get_node_types(conn)
    return render_template("node_single.html", node=node, node_types=node_types)


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
