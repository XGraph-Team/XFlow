begin;
drop table if exists redundant_splits;
drop table if exists simplified_splits;
create table redundant_splits (
    line_id integer array,
    station_id integer array
);

create table simplified_splits (
    new_id integer primary key,
    station_id integer array[2],
    old_id integer array,
    simple_extent geometry(linestring, 3857),
    original_extents geometry(multilinestring, 3857),
    distortion float
);


-- select distinct stations so that we don't add double simplified lines on beads-on-a-string
insert into redundant_splits (station_id, line_id)
     select distinct array[least(j.station_id, c.station_id), greatest(j.station_id, c.station_id)],
                     array_agg(e.line_id order by e.line_id)
        from topology_nodes j
        join topology_edges e on e.line_id = any(j.line_id)
        join topology_nodes c on c.station_id = any(e.station_id)
       where j.topology_name = 'joint' and c.station_id != j.station_id
       group by j.station_id, c.station_id having count(distinct e.line_id) > 1;

with split_simplify_candidates (line_id, station_id, simple_extent, original_length, original_extents) as (
    select line_id, r.station_id, st_shortestline(a.area, b.area),
           (select avg(st_length(line_extent)) from topology_edges e where e.line_id = any(r.line_id)),
           (select st_multi(st_union(line_extent)) from topology_edges e where e.line_id = any(r.line_id))
      from redundant_splits r
      join power_station a on a.station_id = r.station_id[1]
      join power_station b on b.station_id = r.station_id[2]
)
insert into simplified_splits (new_id, station_id, old_id, simple_extent, original_extents, distortion)
     select nextval('line_id'), station_id, line_id,
            simple_extent, original_extents,
            abs(original_length - st_length(simple_extent))
       from split_simplify_candidates
      where abs(original_length - st_length(simple_extent)) < :merge_distortion;

insert into derived_objects (derived_id, derived_type, operation, source_id, source_type)
     select new_id, 'l', 'merge', old_id, 'l'
       from simplified_splits;

-- edges are only ever replaced, never removed, so we don't need to do a pruning step

insert into topology_edges (line_id, station_id, line_extent)
     select new_id, s.station_id, simple_extent
       from simplified_splits s;

update topology_nodes n set line_id = array_replace(n.line_id, r.old_id, r.new_id)
   from (
        select station_id, array_agg(distinct old_id), array_agg(distinct new_id) from (
            select station_id[1], unnest(old_id), new_id from simplified_splits
            union
            select station_id[2], unnest(old_id), new_id from simplified_splits
        ) f (station_id, old_id, new_id) group by station_id
   ) r(station_id, old_id, new_id) where n.station_id = r.station_id;

delete from topology_edges where line_id in (select unnest(old_id) from simplified_splits);
commit;
