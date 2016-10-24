-- Edges are the connectors between assets in an infrastructure network and in
-- the case of transport the assets that enable movement (e.g. roads, rail,
-- cables, water transfer pipes)
CREATE TABLE sos_i_edges (
    edge_id serial PRIMARY KEY -- Primary key and id field for table records
    , edge_name text -- Name of edge asset eg. A40
    , sector text -- Infrastructure sector, eg transport, electricity, water
    , from_node_id integer -- Node id from which the edge begins
    , to_node_id integer -- Node id where the edge ends
    , last_updated timestamp with time zone DEFAULT now() -- Date that this data was last updated
    , data_source_id integer -- Data grouped by source
    , ref_key text -- Tracking code or number for connection to external data reference
    , location geography(LINESTRING, 4326) -- Edge geometry (as a line, could be as minimal as two points)
);