-- Nodes are the infrastructure assets that make of all infrastructure networks
--  (e.g. power generators, reservoirs, incinerators)
CREATE TABLE sos_i_nodes (
    node_id serial PRIMARY KEY -- Primary key and id field for table records
    , node_name text -- Name of node asset, if more than one exists per region and network
    , type text -- Node type (e.g. INTER, PUMP, CCGT, etc.) -- could normalize to (integer) foreign key to nodetype_id in SoS_LU_EntityTypes
    , function text -- Node function (source, sink, intermediate, demand)
    , last_updated timestamp with time zone -- Date that this data was last updated
    , data_source_id integer -- Data grouped by source, Foreign key to area_id in SoS_LU_Data_Source
    , ref_key text -- Tracking code or number for connection to external data reference
    , location geography(POINT, 4326) -- Node geometry (GIS location, shape)
);

-- create geographical index
CREATE INDEX sos_i_nodes_gist ON sos_i_nodes USING GIST ( location );
