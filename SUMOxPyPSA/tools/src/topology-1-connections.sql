begin;
drop table if exists topology_connections;
drop table if exists problem_lines;
drop table if exists topology_edges;
drop table if exists topology_nodes;
drop table if exists topology_generators;
drop table if exists dangling_lines;


create table topology_connections (
    line_id integer,
    station_id integer
);

create table problem_lines (
    line_id integer,
    station_id integer array,
    line_extent geometry(linestring, 3857),
    line_terminals geometry(geometry, 3857),
    station_area geometry(geometry, 3857)
);

create table dangling_lines (
    line_id integer,
    extent geometry(linestring, 3857)
);

create table topology_edges (
    line_id integer primary key,
    station_id integer array,
    line_extent geometry(linestring, 3857),
    topology_name varchar(64)
);

create table topology_nodes (
    station_id integer primary key,
    line_id integer array,
    station_location geometry(point, 3857),
    topology_name varchar(64)
);

create table topology_generators (
    station_id integer not null,
    generator_id integer not null,
    primary key (station_id, generator_id)
);

create index topology_edges_station_id on topology_edges using gin(station_id);
create index topology_nodes_line_id    on topology_nodes using gin(line_id);

insert into topology_connections (line_id, station_id)
     select line_id, station_id
       from power_line
       join power_station
         on st_dwithin(st_startpoint(extent), area, radius[1]) or
            st_dwithin(st_endpoint(extent), area, radius[2]);

insert into topology_edges (line_id, station_id, line_extent, topology_name)
   select c.line_id, c.station_id, l.extent, l.power_name from (
        select line_id, array_agg(station_id) from topology_connections group by line_id having count(*) = 2
    ) c (line_id, station_id)
    join power_line l on c.line_id = l.line_id;

insert into topology_nodes (station_id, line_id, station_location, topology_name)
     select s.station_id, array_agg(e.line_id), st_centroid(s.area), s.power_name
       from power_station s
       join topology_edges e on s.station_id = any(e.station_id)
      group by s.station_id;


insert into problem_lines (line_id, station_id, line_extent, line_terminals, station_area)
     select c.line_id, c.station_id, extent,
         st_multi(st_union(st_buffer(st_startpoint(extent), radius[1]), st_buffer(st_endpoint(extent), radius[2]))),
         (select st_union(area) from power_station s where station_id = any(c.station_id)) from (
              select line_id, array_agg(station_id) from topology_connections group by line_id having count(*) > 2
         ) c (line_id, station_id)
         join power_line l on l.line_id = c.line_id;

insert into dangling_lines (line_id, extent)
    select line_id, extent from power_line where line_id not in (
       select line_id from topology_edges
       union all
       select line_id from problem_lines
   );

insert into topology_generators (generator_id, station_id)
     select generator_id,
            (select n.station_id from power_station s
               join topology_nodes n on n.station_id = s.station_id
              where n.topology_name != 'joint'
              order by g.location <-> s.area limit 1)
       from power_generator g;
commit;
