-- A list of data that has been imported into the system using the import tool
CREATE TABLE sos_lu_data_sources (
    data_source_id serial PRIMARY KEY -- Primary key and id field for table records
    , name text -- Short name for the data, eg central pop data
    , description text -- Detailed description of the data, eg The central population scenario data
    , url text -- URL (or filename) of the data source, eg http://download.geofabrik.de/asia/israel-and-palestine-latest.osm.pbf
);