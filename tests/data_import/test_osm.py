from data_import.osm import NodeHandler
from imposm.parser import OSMParser
import pytest
import os

def test_location_to_wkt():
    node_handler = NodeHandler()
    wkt = node_handler.location_as_wkt((0,1))
    assert wkt == "POINT(0.0 1.0)"

def test_location_to_wkt_round():
    node_handler = NodeHandler()
    wkt = node_handler.location_as_wkt((0.123456789,1.987654321))
    assert wkt == "POINT(0.12345679 1.98765432)"

def test_save_bank(capfd):
    """Test saving a bank node
    """
    # set up to parse `bank.osm`
    input_filepath = os.path.join(os.path.dirname(__file__),"data","bank.osm")
    node_handler = NodeHandler()
    p = OSMParser(nodes_callback=node_handler.nodes)
    p.parse(input_filepath)

    # don't use db, so expect tab-separated STDOUT
    resout, reserr = capfd.readouterr()
    assert resout == '1\tBank of Testing\tbank\tPOINT(10.0 50.0)\n'