select count(*) from (
	select distinct unnest(line_id) from topology_nodes
) f (line_id) where line_id not in (select line_id from topology_edges);
select count(*) from (
	select distinct unnest(station_id) from topology_edges
) f (station_id) where station_id not in (select station_id from topology_nodes);