# -*- coding: utf-8 -*-
"""Sources and provenance for infrastructure data
"""
from __future__ import print_function

class Source:
    """A data source

    Each piece of data imported should have a source, e.g. OpenStreetMap
    extract, shapefile provided by NGO.

    Attributes: id, name, description, url
    """
    def __init__(self):
        self.id = 0
        self.name = ""
        self.description = ""
        self.url = ""

def get_source_by_short_name(conn, short_name):
    sql = """SELECT data_source_id, name, description, url
    FROM sos_lu_data_sources
    WHERE name = %s
    """
    cur = conn.cursor()
    cur.execute(sql, (short_name,))

    if cur.rowcount > 1:
        raise ValueError("Source short name was not unique in the database")
    if cur.rowcount == 0:
        raise ValueError("Source short name does not exist in the database")

    data = cur.fetchone()
    source = Source()
    source.id = data[0]
    source.name = data[1]
    source.description = data[2]
    source.url = data[3]

    return source