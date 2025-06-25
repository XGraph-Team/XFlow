#!/bin/bash


if [ -z "$1" ] || [ ! -f "$1" ]
then
    echo Please pass OSM datafile as argument
    exit 1
fi
OSM_DATAFILE=$1

if [ -z "$PGDATABASE" ]
then
    if [ -z "$2" ]
    then
        echo Please pass database name as second argument
        exit 1
    else
        export PGDATABASE=$2
    fi
fi

if [ -n "$PGPORT" ]
then
    # osm2pgsql needs an explicit --port parameter
    OSM2PGSQL_FLAGS=--port=$PGPORT
fi

dropdb --if-exists $PGDATABASE || exit 1
createdb $PGDATABASE || exit 1
psql -c 'CREATE EXTENSION postgis;' || exit 1
psql -c 'CREATE EXTENSION hstore;' || exit 1
osm2pgsql -d $PGDATABASE -c -k -s \
    -S ./power.style \
    --number-processes 1 \
    $OSM2PGSQL_FLAGS \
    $OSM_DATAFILE || exit 1

source ./reset.sh
