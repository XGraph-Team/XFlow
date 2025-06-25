#!/bin/bash

source src/defaults.conf
if [ -f ./gridkit.conf ]
then
    source ./gridkit.conf
fi

# run postgresql with 'safe mode'
shopt -s expand_aliases
alias psql='psql -v ON_ERROR_STOP=1'
# shared node algorithms before any others
psql -f src/node-1-find-shared.sql || exit 1
psql -v terminal_radius=$GRIDKIT_TERMINAL_RADIUS \
     -f src/node-2-merge-lines.sql || exit 1
psql -f src/node-3-line-joints.sql || exit 1

# spatial algorithms benefit from reduction of work from shared node
# algorithms
psql -f src/spatial-1-merge-stations.sql || exit 1
psql -f src/spatial-2-eliminate-line-overlap.sql || exit 1
psql -f src/spatial-3-attachment-joints.sql || exit 1
psql -f src/spatial-4-terminal-intersections.sql || exit 1
psql -f src/spatial-5-terminal-joints.sql || exit 1
psql -f src/spatial-6-merge-lines.sql || exit 1

# topological algorithms
psql -f src/topology-1-connections.sql || exit 1
psql -f src/topology-2-dangling-joints.sql || exit 1
psql -v merge_distortion=$GRIDKIT_MERGE_DISTORTION \
     -f src/topology-3-redundant-splits.sql || exit 1
psql -f src/topology-4-redundant-joints.sql || exit 1

# process electrical tags
psql -f src/electric-1-tags.sql || exit 1
psql -f src/electric-2-patch.sql || exit 1
psql -f src/electric-3-line.sql || exit 1
psql -f src/electric-4-station.sql || exit 1
# abstract network
psql -f src/abstraction-1-high-voltage-network.sql || exit 1
psql -f src/abstraction-2-export.sql || exit 1
