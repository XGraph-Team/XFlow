#!/bin/bash
psql -c "COPY network_bus TO STDOUT WITH CSV HEADER QUOTE ''''" > buses.csv
psql -c "COPY network_link TO STDOUT WITH CSV HEADER QUOTE ''''" > links.csv
psql -c "COPY network_generator TO STDOUT WITH CSV HEADER QUOTE ''''" > generators.csv
psql -c "COPY network_transformer TO STDOUT WITH CSV HEADER QUOTE ''''" > transformers.csv

zip entsoe.zip README.md buses.csv links.csv generators.csv transformers.csv
