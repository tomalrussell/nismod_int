# -*- coding: utf-8 -*-
"""Infrastructure nodes: assets and points of demand
"""
from __future__ import print_function

class Node:
    """A node in the infrastructure network
    """
    def __init__(self, data):
        self.id = data["node_id"]
        self.name = data["node_name"].decode("utf-8")
        self.lon = data["lon"]
        self.lat = data["lat"]
        self.type = data["type"]
        self.status = data["status"]