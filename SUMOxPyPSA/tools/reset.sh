#!/bin/bash

source src/defaults.conf
if [ -f ./gridkit.conf ]
then
    source ./gridkit.conf
fi

psql -f ./src/prepare-functions.sql
psql -v terminal_radius=$GRIDKIT_TERMINAL_RADIUS \
     -v station_buffer=$GRIDKIT_STATION_BUFFER \
     -f ./src/prepare-tables.sql
