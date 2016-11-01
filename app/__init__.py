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
from node import Node, get_nodes
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

def get_conn():
    return psycopg2.connect("dbname=vagrant user=vagrant", cursor_factory=psycopg2.extras.DictCursor)

@app.route("/nodes")
def nodes_page():
    """List nodes
    """
    with get_conn() as conn:
        # todo: include search/filter form, GET variables
        nodes = get_nodes(conn)

    return render_template("node_list.html", nodes=nodes)

@app.route("/nodes/<node_id>", methods=['GET', 'POST'])
def node_page(node_id):
    """Node details
    """
    node, node_types = get_node_and_types(node_id)
    is_edit = request.args.get('edit') == "true"

    if not is_edit:
        return render_template("node_single.html", node=node)

    if request.method == 'POST':
        data = request.form
        if data.get("x-method") == "DELETE":
            with get_conn() as conn:
                node.delete(conn)

            return render_template("deleted.html", type="Node")

        else:
            node.set_name(data.get("name"))
            node.set_type(data.get("type"))
            node.set_function(data.get("function"))
            node.set_condition(data.get("condition"))
            with get_conn() as conn:
                node.save(conn)
            return render_template("node_single_edit.html", node=node, node_types=node_types)

    else:
        return render_template("node_single_edit.html", node=node, node_types=node_types)

def get_node_and_types(node_id):
    """Load node and node types for single node page
    """
    try:
        node_id = int(node_id)
    except ValueError:
        abort(404)

    with get_conn() as conn:
        try:
            node = Node().load_by_id(conn, node_id)
        except ValueError:
            abort(404)
        node_types = get_node_types(conn)

    return node, node_types

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
    with get_conn() as conn:
        nodes = get_nodes(conn, area=area_name)
        features = [node.as_geojson_feature_dict() for node in nodes]

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        resp = make_response(json.dumps(geojson), 200)
        resp.headers['Content-Type'] = "application/json"
    return resp

if __name__ == "__main__":
    app.run(port=5050)
