-- Nodes are the infrastructure assets that make of all infrastructure networks
--  (e.g. power generators, reservoirs, incinerators)

-- enum for status of imported data
CREATE TYPE data_status AS ENUM ('staged', 'approved', 'archived');

CREATE TABLE sos_i_nodes (
    node_id serial PRIMARY KEY -- Primary key and id field for table records
    , node_name text -- Name of node asset, if more than one exists per region and network
    , type text -- Node type (e.g. INTER, PUMP, CCGT, etc.) - could normalize to (integer) foreign key to nodetype_id in sos_lu_entity_types
    , area text -- Area where node resides - could normalize to (integer) foreign key to nodetype_id in sos_lu_areas
    , function text -- Node function (source, sink, intermediate, demand)
    , condition text -- Rating of node condition (good, average, poor)
    , last_updated timestamp with time zone DEFAULT now() -- Date that this data was last updated
    , data_source_id integer -- Data grouped by source, Foreign key to area_id in sos_lu_data_source
    , status data_status DEFAULT 'staged' -- Data is staged on import, then manually approved and eventually archived
    , ref_key text -- Tracking code or number for connection to external data reference
    , location geography(POINT, 4326) -- Node geometry (GIS location, shape)
);

-- create geographical index
CREATE INDEX sos_i_nodes_gist ON sos_i_nodes USING GIST ( location );
