"""OpenStreetMap data import
"""
from __future__ import print_function
import os
import sys
import psycopg2
from dotenv import load_dotenv, find_dotenv
from app.edge import Edge

def add_edges_between_types(conn, from_type, to_type, sector):
    with conn.cursor() as cur:
        # get nodes of to_type
        cur.execute("""SELECT node_id
        FROM sos_i_nodes
        WHERE type = %s
        """,
        (to_type, ))
        # each node:
        for node in cur:
            # get nearest node of from_type
            to_node_id = node["node_id"]
            with conn.cursor() as sub_cur:
                sub_cur.execute("""SELECT from_nodes.node_id as node_id
                FROM sos_i_nodes as from_nodes, sos_i_nodes as to_nodes
                WHERE from_nodes.type = %s
                AND to_nodes.node_id = %s
                ORDER BY ST_Distance(from_nodes.location, to_nodes.location) ASC
                LIMIT 1
                """,
                (from_type, to_node_id ))

                for from_node in sub_cur:
                    from_node_id = from_node["node_id"]

                    # add edge from->to given sector
                    e = Edge({
                        "from_node_id": from_node_id,
                        "to_node_id": to_node_id,
                        "sector": sector
                    })
                    e.save(conn)

def main():
    """Initial setup: run this as a script to add edges between
    existing nodes in the database.

    From => To
    is flow of service/commodity
    so 'from' type is likely to be supply nodes
    and 'to' type is likely to be demand nodes

        python -m data_import.depend_on_nearest_of_type electricity_sink water_tower electricity

    """
    if len(sys.argv) != 4:
        print("Usage: python -m data_import.depend_on_nearest_of_type <from_type> <to_type> <sector>")
        exit()

    from_type = sys.argv[1]
    to_type = sys.argv[2]
    sector = sys.argv[3]

    load_dotenv(find_dotenv())
    conn = psycopg2.connect(
        cursor_factory=psycopg2.extras.DictCursor,
        host=os.environ.get("APP_PG_HOST"),
        database=os.environ.get("APP_PG_DATABASE"),
        user=os.environ.get("APP_PG_USER"),
        password=os.environ.get("APP_PG_PASSWORD"),
        port=os.environ.get("APP_PG_PORT")
    )

    add_edges_between_types(conn, from_type, to_type, sector)

    conn.close()

if __name__ == '__main__':
    main()
