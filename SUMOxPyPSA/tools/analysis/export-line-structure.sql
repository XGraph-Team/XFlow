COPY (
    SELECT l.*, st_length(st_transform(e.line_extent, 4326)::geography) as line_length, e.station_id
      FROM line_structure l JOIN topology_edges e ON l.line_id = e.line_id
) TO STDOUT WITH CSV HEADER
