# -*- coding: utf-8 -*-
"""Edges and dependencies in the infrastructure network
"""
from __future__ import print_function
import datetime

class Edge:
    """An edge
    """
    def __init__(self, data=None):
        self.id = None
        self.name = ""
        self.from_node_id = 0
        self.to_node_id = 0
        self.sector = "unknown"
        self.last_updated = datetime.datetime.fromtimestamp(0)
        self.geojson = ""

        if data is not None:
            self._update_from_dict(data)

    def __repr__(self):
        return "Edge:{} {}>{}".format(self.sector, self.from_node_id, self.to_node_id)

    def _update_from_dict(self, data):
        if "edge_id" in data:
            self.id = data["edge_id"]
        if "edge_name" in data and data["edge_name"] is not None:
            self.name = data["edge_name"].decode("utf-8")
        if "last_updated" in data:
            self.last_updated = data["last_updated"]
        if "geojson" in data:
            self.geojson = data["geojson"]

        self.from_node_id = data["from_node_id"]
        self.to_node_id = data["to_node_id"]
        self.sector = data["sector"]

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

    def save(self, conn):
        if self.id is not None:
            self._update(conn)
        else:
            self._save_new(conn)
        conn.commit()
        return self

    def _update(self, conn):
        raise NotImplementedError("Should UPDATE if calling save on an edge that has an id")

    def _save_new(self, conn):
        with conn.cursor() as cur:
            sql = """INSERT INTO sos_i_edges (
                edge_name,
                sector,
                from_node_id,
                to_node_id,
                last_updated
            ) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s
            ) RETURNING edge_id"""

            cur.execute(sql, (
                self.name,
                self.sector,
                self.from_node_id,
                self.to_node_id,
                datetime.datetime.now()
                ))

            data = cur.fetchone()
            self.id = data["edge_id"]

        return self

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
