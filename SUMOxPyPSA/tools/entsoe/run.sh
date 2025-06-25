#!/bin/bash

source entsoe.conf

psql -f ../src/prepare-functions.sql
psql -v terminal_radius=$GRIDKIT_TERMINAL_RADIUS \
     -v station_buffer=$GRIDKIT_STATION_BUFFER \
     -f gridkit-start.sql
psql -f ../src/spatial-1-merge-stations.sql
psql -f ../src/spatial-2-eliminate-line-overlap.sql
psql -f ../src/spatial-3-attachment-joints.sql
psql -f ../src/spatial-4-terminal-intersections.sql
psql -f ../src/spatial-5-terminal-joints.sql
psql -f ../src/spatial-6-merge-lines.sql
psql -f ../src/topology-1-connections.sql
psql -f ../src/topology-2-dangling-joints.sql

psql -v merge_distortion=$GRIDKIT_MERGE_DISTORTION \
     -f ../src/topology-3-redundant-splits.sql
psql -f ../src/topology-4-redundant-joints.sql

psql -f electric-properties.sql
# Fix edges which should not have been merged
psql -f fixup-merge.sql

psql -f abstraction.sql
# Add transformers between DC terminals and stations
psql -v hvdc_distance=$GRIDKIT_HVDC_DISTANCE \
     -f fixup-hvdc.sql

bash ./export.sh
echo "All done"
