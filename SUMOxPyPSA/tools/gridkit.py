#!/usr/bin/env python
"""GridKit is a power grid extraction toolkit.

Usage:
    python gridkit.py path/to/data-file.osm --filter \\
         --poly path/to/area.poly \\
         --pg user=gridkit database=gridkit

GridKit will create a database, import the power data, run the
extraction procedures, and write CSV's with the high-voltage network
extract.
"""
from __future__ import print_function, unicode_literals, division
import os, sys, io, re, csv, argparse, logging, subprocess, functools, getpass, operator
from util.postgres import PgWrapper as PgClient, PSQL
from util.which import which

__author__ = 'Bart Wiegmans'

if sys.version_info >= (3,0):
    raw_input = input




def ask(question, default=None, type=str):
    if default is not None:
        question = "{0} [{1}]".format(question, default)
    try:
        value = raw_input(question + ' ')
    except KeyboardInterrupt:
        print('')
        quit(1)
    if not value:
        return default
    try:
        return type(value)
    except ValueError:
        return None

def ask_db_params(pg_client, database_params):
    while not pg_client.check_connection():
        print("Please provide the PostgreSQL connection parameters (press Ctrl+C to exit)")
        user = ask("PostgreSQL user name:", default=(database_params.get('user') or getpass.getuser()))
        host = ask("PostgreSQL hostname:", default=(database_params.get('host') or 'localhost'))
        port = ask("PostgreSQL port number:", type=int, default=(database_params.get('port') or 5432))
        dbnm = ask("PostgreSQL database:", type=str, default=(database_params.get('database') or user))
        new_params = database_params.copy()
        new_params.update(user=user, host=host, port=port, database=dbnm)
        pg_client.update_params(new_params)
    print("Connection succesful")
    database_params.update(**new_params)

def setup_database(pg_client, database_name, interactive):
    io_handle = io.StringIO()
    pg_client.do_getcsv('SELECT datname FROM pg_database', io_handle)
    io_handle.seek(0,0)
    databases = list(map(operator.itemgetter(0), csv.reader(io_handle)))

    while interactive and database_name in databases:
        overwrite = ask("Database {0} exists. Overwrite [y/N]?".format(database_name),
                        type=lambda s: s.lower().startswith('y'))
        if overwrite:
           break
        database_name = ask("Database name:", default='gridkit')
    if not database_name in databases:
        pg_client.do_createdb(database_name)
    pg_client.update_params({'database': database_name})
    pg_client.check_connection()
    pg_client.do_query('CREATE EXTENSION IF NOT EXISTS hstore;')
    pg_client.do_query('CREATE EXTENSION IF NOT EXISTS postgis;')
    print("Database", database_name, "set up")
    return database_name

def do_import(osm_data_file, database_name, database_params):
    if 'password' in database_params:
        os.environ['PGPASS'] = database_params['password']
    command_line = [OSM2PGSQL, '-d', database_name,
                    '-c', '-k', '-s', '-S', POWERSTYLE]
    if 'port' in database_params:
        command_line.extend(['-P', str(database_params['port'])])
    if 'user' in database_params:
        command_line.extend(['-U', database_params['user']])
    if 'host' in database_params:
        command_line.extend(['-H', database_params['host']])
    command_line.append(osm_data_file)
    logging.info("Calling %s", ' '.join(command_line))
    subprocess.check_call(command_line)

def do_conversion(pg_client, voltage_cutoff=220000):
    f = functools.partial(os.path.join, BASE_DIR, 'src')
    # preparing tables
    logging.info("Preparing tables")
    pg_client.do_queryfile(f('prepare-functions.sql'))
    pg_client.do_queryfile(f('prepare-tables.sql'))

    # shared node algorithms
    logging.info("Shared-node algorithms started")
    pg_client.do_queryfile(f('node-1-find-shared.sql'))
    pg_client.do_queryfile(f('node-2-merge-lines.sql'))
    pg_client.do_queryfile(f('node-3-line-joints.sql'))
    logging.info("Shared-node algorithms finished")

    # spatial algorithms
    logging.info("Spatial algorithms started")
    pg_client.do_queryfile(f('spatial-1-merge-stations.sql'))
    pg_client.do_queryfile(f('spatial-2-eliminate-line-overlap.sql'))
    pg_client.do_queryfile(f('spatial-3-attachment-joints.sql'))
    pg_client.do_queryfile(f('spatial-4-terminal-intersections.sql'))
    pg_client.do_queryfile(f('spatial-5-terminal-joints.sql'))
    pg_client.do_queryfile(f('spatial-6-merge-lines.sql'))
    logging.info("Spatial algorithms finished")

    # topological algoritms
    logging.info("Topological algorithms started")
    pg_client.do_queryfile(f('topology-1-connections.sql'))
    pg_client.do_queryfile(f('topology-2-dangling-joints.sql'))
    pg_client.do_queryfile(f('topology-3-redundant-splits.sql'))
    pg_client.do_queryfile(f('topology-4-redundant-joints.sql'))
    logging.info("Topological algorithms finished")

    logging.info("Electric algorithms started")
    pg_client.do_queryfile(f('electric-1-tags.sql'))
    pg_client.do_queryfile(f('electric-2-patch.sql'))
    pg_client.do_queryfile(f('electric-3-compute.sql'))

    pg_client.do_queryfile(f('electric-4-reference.sql'))
    logging.info("Electric algorithms finished")


    pg_client.do_queryfile(f('topology-3a-assign-tags.sql'))
    pg_client.do_queryfile(f('topology-3b-electrical-properties.sql'))

    with io.open(f('topology-4-high-voltage-network.sql'), 'r') as handle:
        query_text = handle.read().replace('220000', str(voltage_cutoff))
        pg_client.do_query(query_text)

    pg_client.do_queryfile(f('topology-5-abstraction.sql'))
    logging.info("Topological algorithms done")

def export_network_csv(pg_client, full_export=False, base_name='gridkit'):
    logging.info("Running export")
    if full_export:
        with io.open(base_name + '-all-vertices.csv', 'w') as handle:
            pg_client.do_getcsv('heuristic_vertices', handle)
        with io.open(base_name + '-all-links.csv', 'w') as handle:
            pg_client.do_getcsv('heuristic_links', handle)

    with io.open(base_name + '-highvoltage-vertices.csv', 'w') as handle:
        pg_client.do_getcsv('heuristic_vertices_highvoltage', handle)

    with io.open(base_name + '-highvoltage-links.csv', 'w') as handle:
        pg_client.do_getcsv('heuristic_links_highvoltage', handle)

    logging.info("Export done")


def file_age_cmp(a, b):
    # negative if a is younger than b, positive if a is older than b
    return os.path.getmtime(b) - os.path.getmtime(a)


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s [%(asctime)s] / %(message)s', level=logging.INFO)


    OSM2PGSQL  = which('osm2pgsql')
    OSMCONVERT = which('osmconvert')
    OSMFILTER  = which('osmfilter')
    OSMOSIS    = which('osmosis')
    BASE_DIR   = os.path.realpath(os.path.dirname(__file__))
    POWERSTYLE = os.path.join(BASE_DIR, 'power.style')

    parse_pair = lambda s: tuple(s.split('=', 1))
    ap = argparse.ArgumentParser()
    # polygon filter files
    ap.add_argument('--filter', action='store_true', help='Filter input file for power data (requires osmfilter)')
    ap.add_argument('--poly',type=str,nargs='+', help='Polygon file(s) to limit the areas of the input file (requires osmconvert)')
    ap.add_argument('--no-interactive', action='store_false', dest='interactive', help='Proceed automatically without asking questions')
    ap.add_argument('--no-import', action='store_false', dest='_import', help='Skip import step')
    ap.add_argument('--no-conversion', action='store_false', dest='convert', help='Skip conversion step')
    ap.add_argument('--no-export', action='store_false', dest='export', help='Skip export step')
    ap.add_argument('--pg', type=parse_pair, default=[], nargs='+', help='Connection arguments to PostgreSQL, eg. --pg user=gridkit database=europe')
    ap.add_argument('--psql', type=str, help='Location of psql binary', default=PSQL)
    ap.add_argument('--osm2pgsql', type=str, help='Location of osm2pgsql binary', default=OSM2PGSQL)
    ap.add_argument('--voltage', type=int, help='High-voltage cutoff level', default=220000)
    ap.add_argument('--full-export', action='store_true', dest='full_export')
    ap.add_argument('osmfile', nargs='?')
    args = ap.parse_args()

    # i've added this for the scigrid folks
    PSQL        = args.psql
    OSM2PGSQL   = args.osm2pgsql
    osmfile     = args.osmfile
    interactive = args.interactive and os.isatty(sys.stdin.fileno())
    if args._import and args.osmfile is None:
        ap.error("OSM source file required")

    if args.filter:
        if not OSMFILTER:
            logging.error("Cannot find osmfilter executable, necessary for --filter")
            quit(1)
        name, ext = os.path.splitext(osmfile)
        new_name  = name + '-power.o5m'
        logging.info("Filtering %s to make %s", osmfile, new_name)
        subprocess.check_call([OSMFILTER, osmfile, '--keep="power=*"', '-o=' + new_name])
        osmfile  = new_name

    # get effective database parameters
    db_params = dict((k[2:].lower(), v) for k, v in os.environ.items() if k.startswith('PG'))
    db_params.update(**dict(args.pg))

    # need 'root' database for polyfile based extraction
    if args.poly:
        db_params.update(database=db_params.get('user') or 'postgres')

    pg_client = PgClient()
    pg_client.update_params(db_params)

    if pg_client.check_connection():
        logging.info("Connection OK")
    elif interactive and not args.poly:
        logging.warn("Cannot connect to database")
        ask_db_params(pg_client, db_params)
    else:
        logging.error("Cannot connect to database")
        quit(1)


    if OSM2PGSQL is None or not (os.path.isfile(OSM2PGSQL) and os.access(OSM2PGSQL, os.X_OK)):
        logging.error("Cannot find osm2pgsql executable")
        quit(1)


    if args.poly:
        osmfiles = dict()
        for polyfile in args.poly:
            if not os.path.isfile(polyfile):
                logging.warn("%s is not a file", polyfile)
                continue
            polygon_name, ext = os.path.splitext(os.path.basename(polyfile))
            osmfile_name, ext = os.path.splitext(osmfile)
            osmfile_for_area = '{0}-{1}.o5m'.format(osmfile_name, polygon_name)
            if os.path.isfile(osmfile_for_area) and file_age_cmp(osmfile_for_area, osmfile) < 0:
                logging.info("File %s already exists and is newer than %s", osmfile_for_area, osmfile)
            else:
                logging.info("Extracting area %s from %s to make %s", polygon_name, osmfile, osmfile_for_area)
                subprocess.check_call([OSMCONVERT, osmfile, '--complete-ways', '-B='+polyfile, '-o='+osmfile_for_area])
            osmfiles[polygon_name] = osmfile_for_area

        for area_name, area_osmfile in osmfiles.items():
            # cleanup the name for use as a database name
            database_name = 'gridkit_' + re.sub('[^A-Z0-9]+', '_', area_name, 0, re.I)
            # select 'postgres' database for creating other databases
            pg_client.update_params({'database':'postgres'})
            pg_client.check_connection()
            setup_database(pg_client, database_name, False)
            # setup-database automatically uses the right connection
            do_import(area_osmfile, database_name, db_params)
            do_conversion(pg_client, args.voltage)
            export_network_csv(pg_client, args.full_export, database_name)

    else:
        database_name = db_params.get('database') or db_params.get('postgres')
        if database_name is None:
            # last case fallback
            osmfile_name, ext = os.path.splitext(os.path.basename(osmfile))
            database_name = re.sub(r'[^A-Z0-9_]+', '_', osmfile_name.lower(), 0, re.I)
        if args._import:
            database_name = setup_database(pg_client, database_name, interactive)
            do_import(osmfile, database_name, db_params)
        if args.convert:
            try:
                do_conversion(pg_client, args.voltage)
            except KeyboardInterrupt:
                logging.warn("Execution interrupted - process is not finished")
                quit(1)
        if args.export:
            export_network_csv(pg_client, args.full_export, database_name or 'gridkit')
