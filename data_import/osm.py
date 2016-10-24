"""OpenStreetMap data import
"""
from __future__ import print_function
import datetime
import os
import sys
import psycopg2
from dotenv import load_dotenv, find_dotenv
from imposm.parser import OSMParser
import app.source

class NodeHandler(object):
    """Handle the parsed OSM data

    Holds a database connection and inserts each item to the database.
    Otherwise outputs parsed matching nodes to STDOUT.
    """
    def __init__(self):
        self._conn = None
        self._data_source_id = None
        self._area_short_name = None

    def connection(self, conn):
        self._conn = conn

    def source(self, source_id):
        self._data_source_id = source_id

    def area(self, area_short_name):
        self._area_short_name = area_short_name

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
                    self._save_node(osmid, "waste_water_treatment", name, location)

                elif man_made_type == 'water_works':
                    self._save_node(osmid, "water_treatment", name, location)

    def _save_node(self, node_id, node_type, name, location):
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
                            last_updated,
                            data_source_id,
                            area
                        ) VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )""",
                        (
                            node_id,
                            name,
                            node_type,
                            point,
                            datetime.datetime.now(),
                            self._data_source_id,
                            self._area_short_name
                        ))
            self._conn.commit()
            cur.close()
        else:
            # print to STDOUT
            print("\t".join(map(str,(node_id, name, node_type, point))))

    def location_as_wkt(self, lon_lat_tuple):
        lon = round(lon_lat_tuple[0], 8)
        lat = round(lon_lat_tuple[1], 8)
        return "POINT({} {})".format(lon, lat)

def main():
    """Initial setup: run this as a script to import osm.pbf to postgres,
    for example, with monaco downloaded from Geofabrik:

        python -m app.osm ./monaco-latest.osm.pbf osm_extract monaco

    Possible enhancement: set up nismod_int as a package that exposes an
    `import` command
    """
    if len(sys.argv) != 4:
        print("Usage: python osm.py <path_to_file> <data_source_short_name> <area_short_name>")
        exit()

    path_to_file = sys.argv[1]
    data_source_short_name = sys.argv[2]
    area_short_name = sys.argv[3]

    load_dotenv(find_dotenv())
    conn = psycopg2.connect(
        host=os.environ.get("APP_PG_HOST"),
        database=os.environ.get("APP_PG_DATABASE"),
        user=os.environ.get("APP_PG_USER"),
        password=os.environ.get("APP_PG_PASSWORD"),
        port=os.environ.get("APP_PG_PORT")
    )

    source = app.source.get_source_by_short_name(conn, data_source_short_name)

    node_handler = NodeHandler()
    node_handler.source(source.id)
    node_handler.area(area_short_name)
    node_handler.connection(conn)

    p = OSMParser(nodes_callback=node_handler.nodes)
    p.parse(path_to_file)
    conn.close()

if __name__ == '__main__':
    main()
