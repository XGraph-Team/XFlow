begin;
drop table if exists invalid_merge;
drop table if exists invalid_join;
create table invalid_merge (
    merged_id integer primary key,
    line_id integer array,
    station_id integer array[2]
);

create table invalid_join (
    joined_id integer primary key,
    line_id integer array,
    joint_id integer array
);


insert into invalid_merge (merged_id, line_id, station_id)
     select derived_id, s.line_id, s.station_id
       from redundant_splits s
       join derived_objects o on s.line_id = o.source_id
       join line_structure_conflicts c on c.line_id = o.derived_id
      where o.derived_type = 'l' and o.operation = 'merge';

insert into invalid_join (joined_id, line_id, joint_id)
    select derived_id, source_id,
           array(select joint_id from joint_edge_pair
                  where left_id = any(source_id) or right_id = any(source_id))
      from derived_objects
      join invalid_merge i on i.merged_id = any(source_id);

-- delete prior to insert
delete from topology_edges where line_id in (select unnest(line_id) from invalid_merge union select unnest(line_id) from invalid_join);
delete from topology_nodes where station_id in (select unnest(joint_id) from invalid_join);

-- restore edges and nodes
insert into topology_edges (line_id, station_id, line_extent, topology_name)
     select l.line_id, array(select c.station_id from topology_connections c where c.line_id = l.line_id),
            extent, power_name
       from power_line l
      where exists (select 1 from invalid_join j where l.line_id = any(j.line_id))
         or exists (select 1 from invalid_merge m where l.line_id = any(m.line_id));

insert into topology_nodes (station_id, line_id, station_location, topology_name)
     select s.station_id, array(select c.line_id from topology_connections c where c.station_id = s.station_id),
            st_centroid(area), power_name
       from power_station s
      where exists (select 1 from invalid_join j where s.station_id = any(j.joint_id));

-- remove invalidly merged /joined lines
delete from topology_edges e
      where exists(select 1 from invalid_join where e.line_id = joined_id)
         or exists(select 1 from invalid_merge where e.line_id = merged_id);

-- i reconstructed the edges from 'pristine' connections; now restore the nodes as well
with restored_edges(line_id) as (
     select unnest(line_id) from invalid_join
      union
     select unnest(line_id) from invalid_merge
), affected_stations(station_id) as (
   select unnest(station_id) from topology_edges e
    join restored_edges r on e.line_id = r.line_id
), current_edges (station_id, line_id) as (
    select station_id,
           array(select line_id
                   from topology_edges e
                  where a.station_id = any(e.station_id)
                  order by line_id)
     from affected_stations a
)
update topology_nodes n
   set line_id = c.line_id
  from current_edges c
 where c.station_id = n.station_id;

commit;
