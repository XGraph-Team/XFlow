begin;
drop table if exists terminal_joints;
drop table if exists extended_lines;

create table terminal_joints (
    station_id integer primary key,
    line_id integer array,
    line_pt integer array,
    location geometry(point, 3857)
);

create table extended_lines (
    line_id integer primary key,
    line_pt integer array,
    old_extent geometry(linestring, 3857),
    new_extent geometry(linestring, 3857),
    locations  geometry(multipoint, 3857)
);

with joint_groups (line_id, line_pt, locations) as (
    select array_agg(s.line_id), array_agg(s.line_pt), st_union(st_pointn(l.extent, s.line_pt))
       from terminal_sets s join power_line l on l.line_id = s.line_id
       group by set_key having count(*) > 2
) insert into terminal_joints (station_id, line_id, line_pt, location)
    select nextval('station_id'), line_id, line_pt, st_centroid(locations) from joint_groups;

insert into extended_lines (line_id, line_pt, old_extent, new_extent, locations)
     select j.line_id, array_agg(j.line_pt), l.extent, l.extent, st_multi(st_union(j.location)) from (
         select unnest(line_id), unnest(line_pt), location from terminal_joints
    ) j (line_id, line_pt, location)
      join power_line l on l.line_id = j.line_id
     where not st_dwithin(j.location, st_pointn(l.extent, j.line_pt), 1)
     group by j.line_id, l.extent;

update extended_lines
   set new_extent = case when line_pt[1] = 1 then st_addpoint(new_extent, st_closestpoint(locations, st_startpoint(new_extent)), 0)
                         else st_addpoint(new_extent, st_closestpoint(locations, st_endpoint(new_extent)), -1) end;

update extended_lines
   set new_extent = case when line_pt[2] = 1 then st_addpoint(new_extent, st_closestpoint(locations, st_startpoint(new_extent)), 0)
                         else st_addpoint(new_extent, st_closestpoint(locations, st_endpoint(new_extent)), -1) end
   where array_length(line_pt, 1) = 2;

insert into power_station (station_id, power_name, area)
     select station_id, 'joint', st_buffer(location, 1)
       from terminal_joints;

update power_line l
   set extent = j.new_extent
  from extended_lines j
 where j.line_id = l.line_id;

update power_line l
   set radius = minimal_radius(l.extent, t.locations, l.radius) from (
        select line_id, st_union(location) from (
            select unnest(line_id), location from terminal_joints
        ) f (line_id, location) group by line_id
   ) t (line_id, locations) where t.line_id = l.line_id;

insert into derived_objects (derived_id, derived_type, operation, source_id, source_type)
     select station_id, 's', 'merge', line_id, 'l'
       from terminal_joints;

commit;
