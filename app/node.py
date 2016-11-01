# -*- coding: utf-8 -*-
"""Infrastructure nodes: assets and points of demand
"""
from __future__ import print_function
import datetime

class Node:
    """A node in the infrastructure network
    """
    def __init__(self, data=None):
        self.id = 0
        self.name = ""
        self.lon = 0
        self.lat = 0
        self.type = "unknown"
        self.function = "unknown"
        self.condition = "unknown"
        self.last_updated = datetime.datetime.fromtimestamp(0)
        self.status = None

        if data is not None:
            self._update_from_dict(data)

    def _update_from_dict(self, data):
        self.id = data["node_id"]
        self.name = data["node_name"].decode("utf-8")
        self.lon = data["lon"]
        self.lat = data["lat"]
        self.type = data["type"]
        self.function = data["function"]
        self.condition = data["condition"]
        self.last_updated = data["last_updated"]
        self.set_status(data["status"])

    def load_by_id(self, conn, node_id):
        with conn.cursor() as cur:
            sql = """SELECT
                ST_X(location::geometry) as lon,
                ST_Y(location::geometry) as lat,
                node_id,
                node_name,
                type,
                function,
                condition,
                last_updated,
                status
            FROM sos_i_nodes
            WHERE node_id = %s"""

            cur.execute(sql, (node_id, ))

            if cur.rowcount != 1:
                raise ValueError
            else:
                data = cur.fetchone()
                self._update_from_dict(data)

        return self

    def save(self, conn):
        with conn.cursor() as cur:
            sql = """UPDATE sos_i_nodes SET
                location = 'POINT(%s %s)',
                node_name = %s,
                type = %s,
                function = %s,
                condition = %s,
                status = %s,
                last_updated = %s
            WHERE node_id = %s"""

            cur.execute(sql, (
                self.lon,
                self.lat,
                self.name,
                self.type,
                self.function,
                self.condition,
                self.status,
                datetime.datetime.now(),
                self.id, ))

        return self

    def delete(self, conn):
        if self.status == "staged":
            # only staged nodes can be deleted, otherwise only archive
            with conn.cursor() as cur:
                sql = """DELETE FROM sos_i_nodes
                WHERE node_id = %s"""
                cur.execute(sql, (self.id, ))
        else:
            raise StatusError("This node cannot be deleted (only nodes that are staged can be deleted).")

    def geometry(self):
        return {
            "type": "Point",
            "coordinates": [self.lon, self.lat]
        }

    def as_geojson_feature_dict(self):
        return {
            "type": "Feature",
            "geometry": self.geometry(),
            "properties": {
                "id": self.id,
                "name": self.name,
                "type": self.type,
                "function": self.function,
                "condition": self.condition,
                "last_updated": self.last_updated,
                "status": self.status
            }
        }

    def set_name(self, name):
        self.name = name

    def set_type(self, node_type):
        self.type = node_type

    def set_function(self, node_function):
        self.function = node_function

    def set_condition(self, node_condition):
        self.condition = node_condition

    def set_status(self, status):
        if self.status is None and status in ("staged", "approved", "archived"):
            # status can be set on creation
            self.status = status

        if self.status == "staged" and status == "approved":
            # status can change from staged->approved
            self.status = "approved"

        if self.status == "approved" and status == "archived":
            # status can change from approved->archived
            self.status = "archived"

class StatusError(Exception):
    """Raise when the node's status forbids some action
    """

def get_nodes(conn, area=None):
    """Get a list of nodes
    """
    with conn.cursor() as cur:
        sql = """SELECT
            ST_X(location::geometry) as lon,
            ST_Y(location::geometry) as lat,
            node_id,
            node_name,
            type,
            function,
            condition,
            status,
            last_updated
        FROM sos_i_nodes"""

        if area is not None:
            sql = sql + " WHERE area = %s"
            cur.execute(sql, (area, ))

        else:
            cur.execute(sql)

        nodes = [Node(f) for f in cur]

    return nodes
