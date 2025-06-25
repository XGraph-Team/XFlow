Code (v1.0): [![DOI](https://zenodo.org/badge/20808/bdw/GridKit.svg)](https://zenodo.org/badge/latestdoi/20808/bdw/GridKit)

ENTSO-E extract: [![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.55853.svg)](http://dx.doi.org/10.5281/zenodo.55853)


# GridKit is a power grid extraction toolkit

GridKit uses spatial and topological analysis to transform map objects
from OpenStreetMap into a network model of the electric power
system. It has been developed in the context of the
[SciGRID](http://scigrid.de) project at the
[Next Energy](http://www.next-energy.de/) research institute, to
investigate the possibility of 'heuristic' analysis to augment the
route-based analysis used in SciGRID. This has been implemented as a
series of scripts for the PostgreSQL database using the PostGIS
spatial extensions.

The network model is intended to be used in power systems analysis
applications, for example using the
[PYPOWER](https://rwl.github.io/PYPOWER) system, or the
[PyPSA](https://github.com/FRESNA/PyPSA) toolkit. In general this will
require the following:

* Careful interpretation of results (e.g. power lines and stations may
  have multiple voltages).
* Realistic information on generation and load in the system
  (electrical supply and demand).
* Reasonable, possibly location specific assumptions on the impedance
  of lines, depending on their internal structure. Unlike SciGRID,
  *such assumptions have not yet been applied*.

Of note, PyPSA implements several methods of network simplification,
which is in many cases essential for ensuring that the power flow
computations remain managable.

## Data exports

Data exports created at March 14, 2016 for North America and Europe
can be downloaded from
[zenodo](https://zenodo.org/record/47317). These exports are licensed
under the Open Database License because they derive from OpenStreetMap
data. They follow the same file structure as [SciGRID](http://scigrid.de/).
The file `util/network.py` contains a parser for these files.

## Requirements

* Python (2.7 or higher)
* PostgreSQL (9.4 or higher)
* PostGIS (2.1 or higher)
* osm2pgsql (0.88.1 or higher)
* Optionally psycopg2 (2.6 or higher)
* Optionally [osm-c-tools](https://gitlab.com/osm-c-tools/osmctools)


## How to Use (the simple way)

Download a power extract from enipedia:

    wget http://enipedia.tudelft.nl/OpenStreetMap/EuropePower.zip
    unzip EuropePower.zip

Ensure you have a user for postgresql with permissions to create
databases and modify schemas. For example:

    createuser -d gridkit

Run `gridkit.py`:

    python gridkit.py EuropePower.osm

The `--pg` option takes a series of key=value pairs, which are parsed
into database connection options. For example to connect to a host on
`10.0.0.160` listening on port 9000:

    python gridkit.py --pg host=10.0.0.160 port=9000 EuropePower.osm

The files `gridkit-highvoltage-vertices.csv` contains a CSV file with
all high-voltage stations, and `gridkit-highvoltage-edges.csv`
contains a CSV file with all high-voltage lines. You may use
`--full-export` to export all other lines, too.

## How to Use (the hard way)

Download a full-planet dump from
[planet.openstreetmap.org](http://planet.openstreetmap.org/pbf/) or a
geographically-bounded extract from
[geofabrik](http://download.geofabrik.de/).

Extract the power information

    osmconvert my_area.osm.pbf -o=my_area.o5m
    osmfilter my_area.o5m --keep='power=*' -o=my_area_power.o5m

Alternatively for extracting a specific region from the planet file
(my\_area.poly should a
[polygon filter file](http://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format),
which you can acquire from
[polygons.openstreetmap.fr](http://polygons.openstreetmap.fr)):

    osmconvert planet-latest.osm.pbf -B=my_area.poly -o=my_area.o5m

### PostgreSQL configuration

GridKit assumes that you have the `psql` and `osm2pgsql` binaries
available. Configuring access to the postgresql server is implemented
using standard
[environment variables](http://www.postgresql.org/docs/9.4/static/libpq-envars.html). Thus,
prior to importing the openstreetmap source data, you should use something like:

    export PGUSER=my_username PGDATABASE=my_database PGPASSWORD=my_password

Optionally also:

    export PGHOST=server_hostname PGPORT=server_port

For more information, check out the linked documentation.

### Extraction process

Import data using the script:

    ./import-data.sh /path/to/data.o5m database_name

The `database_name` parameter is optional if the `PGDATABASE`
environment variable has been set. Running the extraction process is just:

    ./run.sh

You should expect this, depending on your machine and the size of your
dataset, to take anywhere from 5 minutes to a few hours. Afterwards,
you can extract a copy of the network using:

    psql -f export-topology.sql

Which will copy the network to a set of CSV files in `/tmp`:

* `/tmp/heuristic_vertices.csv` and `/tmp/heuristic_links.csv` contain
  the complete network at all voltage and frequency levels.

* `/tmp/heuristic_vertices_highvoltage` and
  `/tmp/heuristic_links_highvoltage` contain the high-voltage network
  (>220kV) at any frequency which is not 16.7Hz.


### Some things to watch out for

This process requires a lot of memory and significant amounts of CPU
time. It also makes *a lot of copies* of the same data. This is very
useful for investigating issues and tracking changes by the system. It
also means that you should probably not use this on
resource-constrained systems, such as docker containers in constrained
virtual machines or raspberry pi's.

Queries have been typically optimized to make the best possible use of
indices, but whether they are actually used is sensitive to query
planner specifics. Depending on the specifics,
[PostgreSQL tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
may be necessary to run the extraction process efficiently.

The resultant network will in almost all cases be considerably more
complex than equivalent networks (e.g. from SciGRID or the
[Bialek model](http://www.powerworld.com/knowledge-base/updated-and-validated-power-flow-model-of-the-main-continental-european-transmission-network). For
practical applications, it is highly advisable to use simplification.


## Analysis Utilities

Aside from the main codebase, some utilities have been implemented to
enable analysis of the results. Notably:

* `util/network.py` allows for some simple analysis of the network,
  transformation into a **PYPOWER** powercase dictionary, and
  'patching' of the network to propagate voltage and frequency
  information from neighbors.
* `util/load_polyfile.py` transforms a set of `poly` files into import
  statements for PostgreSQL, to allow data statistics per area, among
  other things.



