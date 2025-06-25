#!/usr/bin/env python
from __future__ import print_function, unicode_literals
import operator
import psycopg2
import psycopg2.extras
import io
import json
import sys
import logging


CREATE_TABLES = '''
CREATE EXTENSION IF NOT EXISTS hstore;
CREATE EXTENSION IF NOT EXISTS postgis;
DROP TABLE IF EXISTS feature_points;
DROP TABLE IF EXISTS feature_lines;
DROP TABLE IF EXISTS feature_multilines;
CREATE TABLE feature_points (
    import_id serial primary key,
    point geometry(point, 4326),
    properties hstore
);
CREATE TABLE feature_lines (
    import_id serial primary key,
    line  geometry(linestring, 4326),
    properties hstore
);
CREATE TABLE feature_multilines (
    import_id serial primary key,
    multiline geometry(multilinestring, 4326),
    properties hstore
)
'''

INSERT_STATEMENT = {
    'Point': 'INSERT INTO feature_points (point, properties) VALUES (ST_SetSRID(ST_GeomFromText(%s), 4326), %s);',
    'LineString': 'INSERT INTO feature_lines (line, properties) VALUES (ST_SetSRID(ST_GeomFromText(%s), 4326), %s);',
    'MultiLineString': 'INSERT INTO feature_multilines (multiline, properties) VALUES (ST_SetSRID(ST_GeomFromText(%s), 4326), %s);',
}

REMOVE_DUPLICATES = '''
DELETE FROM feature_lines WHERE import_id IN (
    SELECT b.import_id
      FROM feature_lines a, feature_lines b
     WHERE a.import_id < b.import_id
       AND a.properties = b.properties
       AND a.line = b.line
);
'''

SPLIT_MULTILINES = '''
INSERT INTO feature_lines (line, properties)
     SELECT (ST_Dump(multiline)).geom, properties
       FROM feature_multilines;
'''

def hstore(d):
    return dict((unicode(k), unicode(v)) for k, v, in d.items())

def wkt(g):
    def coords(c):
        if isinstance(c[0], list):
            if isinstance(c[0][0], list):
                f = '({0})'
            else:
                f = '{0}'
            t = ', '.join(f.format(a) for a in map(coords, c))
        else:
            t = '{0:f} {1:f}'.format(*c)
        return t
    return '{0:s} ({1:s})'.format(g['type'].upper(), coords(g['coordinates']))


def import_feature(cur,feature_data):
    if feature_data.get('type') == 'FeatureCollection':
        for feature in feature_data['features']:
            import_feature(cur, feature)
    elif feature_data.get('type') == 'Feature':
        cur.execute(INSERT_STATEMENT[feature_data['geometry']['type']],
                    (wkt(feature_data['geometry']),
                     hstore(feature_data['properties'])))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    con = psycopg2.connect('')
    # create table
    with con:
        with con.cursor() as cur:
            cur.execute(CREATE_TABLES)

    # use hstore to store attributes
    psycopg2.extras.register_hstore(con)


    if len(sys.argv) == 1:
        handles = [sys.stdin]
    else:
        handles = [io.open(a,'r') for a in sys.argv[1:]]
    for handle in handles:
        with handle:
            feature_data = json.load(handle)
        with con:
            with con.cursor() as cur:
                import_feature(cur, feature_data)
                cur.execute(SPLIT_MULTILINES)
                cur.execute(REMOVE_DUPLICATES)
            con.commit()
