# -*- coding: utf-8 -*-
"""Infrastructure node types: classes of asset
"""
from __future__ import print_function

def get_node_types(conn):
    sql = """SELECT DISTINCT type
    FROM sos_i_nodes
    """
    cur = conn.cursor()
    cur.execute(sql)

    return [row[0] for row in cur]