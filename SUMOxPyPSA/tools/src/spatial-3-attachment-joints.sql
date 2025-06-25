begin;
-- Get attachment points, split lines, insert stations for attachment points
drop table if exists line_attachments;
drop table if exists attachment_joints;
drop table if exists attachment_split_lines;
drop table if exists attached_lines;

create table line_attachments (
    extent_id  integer not null,
    attach_id  integer not null,
    extent     geometry(linestring, 3857),
    terminal   geometry(point, 3857),
    attachment geometry(point, 3857)
);

create table attachment_joints (
    station_id integer not null,
    line_id    integer array,
    location   geometry(point, 3857)
);

create table attachment_split_lines (
    new_id      integer primary key,
    old_id      integer not null,
    extent      geometry(linestring, 3857),
    attachments geometry(multipolygon, 3857)
);

create table attached_lines (
    line_id     integer primary key,
    old_extent  geometry(linestring, 3857),
    new_extent  geometry(linestring, 3857),
    terminals   geometry(multipoint, 3857),
    attachments geometry(multipoint, 3857)
);

create index attachment_joints_location on attachment_joints using gist (location);

-- startpoint attachments
insert into line_attachments (extent_id, attach_id, extent, terminal, attachment)
   select distinct on (b.line_id) a.line_id, b.line_id, a.extent, st_startpoint(b.extent), st_closestpoint(a.extent, st_startpoint(b.extent))
       from power_line a
       join power_line b on st_dwithin(a.extent, st_startpoint(b.extent), b.radius[1])
        and not (st_dwithin(st_startpoint(a.extent), st_startpoint(b.extent), b.radius[1])
              or st_dwithin(st_endpoint(a.extent), st_startpoint(b.extent), b.radius[1]))
        and not exists (select 1 from power_station s where st_dwithin(s.area, st_startpoint(b.extent), b.radius[1]))
        order by b.line_id, st_distance(a.extent, st_startpoint(b.extent)) asc;

-- endpoint attachments
insert into line_attachments (extent_id, attach_id, extent, terminal, attachment)
   select distinct on (b.line_id) a.line_id, b.line_id, a.extent, st_endpoint(b.extent), st_closestpoint(a.extent, st_endpoint(b.extent))
       from power_line a
       join power_line b on st_dwithin(a.extent, st_endpoint(b.extent), b.radius[2])
        and not (st_dwithin(st_startpoint(a.extent), st_endpoint(b.extent), b.radius[2])
              or st_dwithin(st_endpoint(a.extent), st_endpoint(b.extent), b.radius[2]))
        and not exists (select 1 from power_station s where st_dwithin(s.area, st_endpoint(b.extent), b.radius[2]))
        order by b.line_id, st_distance(a.extent, st_endpoint(b.extent)) asc;

-- Create segments for the split line
insert into attachment_split_lines (new_id, old_id, extent, attachments)
    select nextval('line_id'), extent_id, (st_dump(st_difference(extent, attachments))).geom, attachments from (
        select extent_id, extent, st_multi(st_buffer(st_union(attachment), 1))
           from line_attachments group by extent_id, extent
    ) f (extent_id, extent, attachments)
    where st_numgeometries(st_difference(extent, attachments)) > 1;


-- Create a station for each attachment point
insert into attachment_joints (station_id, line_id, location)
    select nextval('station_id'), array[extent_id, attach_id], attachment
        from line_attachments;

-- Remove duplicates
delete from attachment_joints where station_id in (
    select greatest(a.station_id, b.station_id) from attachment_joints a, attachment_joints b
        where a.station_id != b.station_id and st_dwithin(a.location, b.location, 1)
);

-- Compute which lines to extend to attach to the power lines
insert into attached_lines (line_id, old_extent, new_extent, terminals, attachments)
    select a.attach_id, l.extent, l.extent, a.terminals, a.attachments
        from (
             select attach_id, st_multi(st_union(terminal)), st_multi(st_union(attachment))
                 from line_attachments group by attach_id
        ) a (attach_id, terminals, attachments)
        join power_line l on a.attach_id = l.line_id;

-- Extend the attached lines to connect cleanly with the attachment station.
update attached_lines
    set new_extent = st_addpoint(new_extent, st_closestpoint(attachments, st_startpoint(new_extent)), 0)
    where st_contains(terminals, st_startpoint(old_extent))
      and not st_dwithin(attachments, st_startpoint(old_extent), 1);

update attached_lines
    set new_extent = st_addpoint(new_extent, st_closestpoint(attachments, st_endpoint(new_extent)), -1)
    where st_contains(terminals, st_endpoint(old_extent))
      and not st_dwithin(attachments, st_endpoint(old_extent), 1);


-- insert joints
insert into power_station (station_id, power_name, area)
     select station_id, 'joint', st_buffer(location, 1)
       from attachment_joints;



-- replace power lines
insert into power_line (line_id, power_name, extent, radius)
     select s.new_id, l.power_name, s.extent,
            minimal_radius(s.extent, s.attachments, l.radius)
       from attachment_split_lines s
       join power_line l on l.line_id = s.old_id;


delete from power_line l where exists (
    select 1 from attachment_split_lines s where l.line_id = s.old_id
);

-- update extended lengths
update power_line l
   set extent = a.new_extent, radius = minimal_radius(a.new_extent, a.attachments, l.radius)
  from attached_lines a
 where a.line_id = l.line_id;


-- track new lines
insert into derived_objects (derived_id, derived_type, operation, source_id, source_type)
     select new_id, 'l', 'split', array[old_id], 'l'
       from attachment_split_lines;

-- and stations
insert into derived_objects (derived_id, derived_type, operation, source_id, source_type)
     select station_id, 's', 'merge', line_id, 'l'
       from attachment_joints;

commit;
