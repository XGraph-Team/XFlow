#!/bin/bash

npm install vt-geojson
export MapboxAccessToken=pk.eyJ1IjoicnVzdHkiLCJhIjoib0FjUkJybyJ9.V9QoXck_1Z18MhpwyIE2Og
./node_modules/vt-geojson/cli.js rusty.cm0b8gzp -z 3 > rusty.cm0b8gzp-z3.geojson
./node_modules/vt-geojson/cli.js rusty.02rit83j -z 3 > rusty.02rit83j-z3.geojson
