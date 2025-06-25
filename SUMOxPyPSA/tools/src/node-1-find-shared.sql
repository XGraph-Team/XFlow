begin;
drop table if exists shared_nodes;
create table shared_nodes (
    node_id bigint,
    way_id  bigint array,
    power_type char(1) array,
    path_idx float array,
    primary key (node_id)
);

insert into shared_nodes (node_id, way_id, power_type, path_idx)
    select node_id, array_agg(way_id order by way_id),
        array_agg(power_type order by way_id),
        array_agg(path_idx order by way_id) from (
        select id, unnest(nodes), power_type,
            (generate_subscripts(nodes, 1)::float - 1.0)/(array_length(nodes, 1)-1)
            from planet_osm_ways
            join power_type_names on power_name = hstore(tags)->'power'
            where array_length(nodes, 1) > 1
    ) f(way_id, node_id, power_type, path_idx)
    group by node_id having count(*) > 1;

commit;
