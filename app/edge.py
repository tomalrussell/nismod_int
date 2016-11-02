# -*- coding: utf-8 -*-
"""Edges and dependencies in the infrastructure network
"""
from __future__ import print_function
import datetime

class Edge:
    """An edge
    """
    def __init__(self, data=None):
        self.id = 0
        self.name = ""
        self.from_node_id = 0
        self.to_node_id = 0
        self.sector = "unknown"
        self.last_updated = datetime.datetime.fromtimestamp(0)
        self.geojson = ""

        if data is not None:
            self._update_from_dict(data)

    def _update_from_dict(self, data):
        self.id = data["edge_id"]
        if data["edge_name"] is not None:
            self.name = data["edge_name"].decode("utf-8")
        self.from_node_id = data["from_node_id"]
        self.to_node_id = data["to_node_id"]
        self.sector = data["sector"]
        self.last_updated = data["last_updated"]
        self.geojson = data["geojson"]

    def geometry(self):
        return self.geojson

    def as_geojson_feature_dict(self):
        return {
            "type": "Feature",
            "geometry": self.geometry(),
            "properties": {
                "id": self.id,
                "name": self.name,
                "sector": self.sector,
                "from_node_id": self.from_node_id,
                "to_node_id": self.to_node_id,
                "last_updated": self.last_updated_timestamp()
            }
        }

    def last_updated_timestamp(self):
        if self.last_updated is not None:
            return self.last_updated.strftime("%a, %d %b %Y %H:%M:%S %z")

def get_edges(conn):
    """Get a list of edges
    """
    with conn.cursor() as cur:
        sql = """SELECT
            edge_id,
            edge_name,
            from_node_id,
            to_node_id,
            sector,
            last_updated,
            st_asgeojson(location) AS geojson
        FROM sos_i_edges"""

        cur.execute(sql)

        edges = [Edge(f) for f in cur]

    return edges
