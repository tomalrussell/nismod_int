from __future__ import print_function
from dotenv import load_dotenv, find_dotenv
from imposm.parser import OSMParser
import psycopg2
import csv
import datetime
import os
import sys

class NodeHandler(object):
    """Handle the parsed OSM data

    Holds a database connection and inserts each item to the database.
    Otherwise outputs parsed matching nodes to STDOUT.
    """
    def __init__(self):
        self._conn = None

    def connection(self, conn):
        self._conn = conn

    def nodes(self, nodes):
        for osmid, tags, location in nodes:
            if 'name' in tags:
                name = tags['name']
            else:
                name = ""

            if 'amenity' in tags:
                amenity_type = tags['amenity']

                if amenity_type == 'bank':
                    self._save_node(osmid, amenity_type, name, location)

                elif amenity_type == 'school':
                    self._save_node(osmid, amenity_type, name, location)

                elif amenity_type == 'hospital':
                    self._save_node(osmid, amenity_type, name, location)

            if 'man_made' in tags:
                man_made_type = tags['man_made']

                if man_made_type == 'tower':
                    if 'tower:type' in tags and tags['tower:type'] == 'communication':
                        self._save_node(osmid, man_made_type, name, location)

                elif man_made_type == 'wastewater_plant':
                    self._save_node(osmid, man_made_type, name, location)

                elif man_made_type == 'water_works':
                    self._save_node(osmid, man_made_type, name, location)

    def _save_node(self, id, node_type, name, location):
        """Output node details
        """
        point = self.location_as_wkt(location)

        if self._conn is not None:
            # save to databases
            cur = self._conn.cursor()
            cur.execute("""INSERT INTO sos_i_nodes
                        (
                            ref_key,
                            node_name,
                            type,
                            location,
                            last_updated
                        ) VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )""",
                        (
                            id,
                            name,
                            node_type,
                            point,
                            datetime.datetime.now()
                        ))
            conn.commit()
            cur.close()
        else:
            # print to STDOUT
            print("\t".join(map(str,(id, name, node_type, point))))

    def location_as_wkt(self, lon_lat_tuple):
        lon = round(lon_lat_tuple[0], 8)
        lat = round(lon_lat_tuple[1], 8)
        return "POINT({} {})".format(lon, lat)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python osm.py <path_to_file>")
        exit()

    input_filepath = sys.argv[1]

    load_dotenv(find_dotenv())
    conn = psycopg2.connect(
        host=os.environ.get("APP_PG_HOST"),
        database=os.environ.get("APP_PG_DATABASE"),
        user=os.environ.get("APP_PG_USER"),
        password=os.environ.get("APP_PG_PASSWORD"),
        port=os.environ.get("APP_PG_PORT")
    )

    node_handler = NodeHandler()
    node_handler.connection(conn)

    p = OSMParser(nodes_callback=node_handler.nodes)
    p.parse(input_filepath)
    conn.close()
