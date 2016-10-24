# -*- coding: utf-8 -*-
"""Regions and areas
"""

class Area:
    """A geographical area

    At a first approximation, these are used to classify data into areas of
    interest: the Gaza strip, South-East England

    Initially corresponding to text field in sos_i_nodes
    TODO: make more general and detailed with sos_lu_areas table
    """
    def __init__(self, name):
        self.name = name

def get_areas(conn):
    """Get list of areas available
    """
    sql = """SELECT DISTINCT area
    FROM sos_i_nodes
    """
    cur = conn.cursor()
    cur.execute(sql)
    return [Area(row[0]) for row in cur]
