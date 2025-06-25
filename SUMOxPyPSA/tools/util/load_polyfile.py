#!/usr/bin/env python
from __future__ import print_function, unicode_literals, division
import argparse
import sys
import os
import io
from polyfile import PolyfileParser
from geometry import Polygon

ap = argparse.ArgumentParser()
ap.add_argument('file', nargs='+', type=str)
ap.add_argument('--table', type=str, default='polygons')
args = ap.parse_args()

polygons = dict()
parser = PolyfileParser()
for file_name in args.file:
    if not os.path.isfile(file_name):
        print("Usage: {0} <files>".format(sys.argv[0]))
    name, ext = os.path.splitext(os.path.basename(file_name))
    try:
        pr = parser.parse(io.open(file_name, 'r').read())
        pl = Polygon(pr[1]['1'])
        polygons[name] = pl.to_wkt()
    except Exception as e:
        print("Could not process {0} because {1}".format(file_name, e), file=sys.stderr)
        quit(1)

values = ','.join("('{0}', ST_SetSRID(ST_GeomFromText('{1}'), 4326))".format(n, p)
                  for (n, p) in polygons.items())

print('''
BEGIN;
DROP TABLE IF EXISTS {0};
CREATE TABLE {0} (
    name varchar(64) primary key,
    polygon geometry(polygon, 4326)
);
INSERT INTO {0} (name, polygon) VALUES {1};
COMMIT;
'''.format(args.table, values))
# of course you can abuse this. don't do that, then
