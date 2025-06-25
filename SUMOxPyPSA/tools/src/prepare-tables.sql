/* assume we use the osm2pgsql 'accidental' tables */
begin transaction;
drop table if exists node_geometry;
drop table if exists way_geometry;
drop table if exists station_polygon;

drop table if exists power_type_names;
drop table if exists power_station;
drop table if exists power_line;
drop table if exists power_generator;

drop table if exists source_tags;
drop table if exists source_objects;
drop table if exists derived_objects;

drop sequence if exists line_id;
drop sequence if exists station_id;
drop sequence if exists generator_id;

create sequence station_id;
create sequence line_id;
create sequence generator_id;

create table node_geometry (
    node_id bigint primary key,
    point   geometry(point, 3857) not null
);

create table way_geometry (
    way_id bigint primary key,
    line   geometry(linestring, 3857) not null
);

create table station_polygon (
    station_id integer primary key,
    polygon    geometry(polygon, 3857) not null
);

-- implementation of source_ids and source_tags table will depend on the data source used
create table source_objects (
    osm_id   bigint not null,
    osm_type char(1) not null,
    power_id integer not null,
    power_type char(1) not null,
    primary key (osm_id, osm_type)
);

-- both ways lookups
create index source_objects_power_idx on source_objects (power_type, power_id);

create table source_tags (
    power_id   integer not null,
    power_type char(1) not null,
    tags       hstore,
    primary key (power_id, power_type)
);

-- NB the arrays are convenient but not necessary
create table derived_objects (
     derived_id integer not null,
     derived_type char(1) not null,
     operation varchar(16) not null,
     source_id integer array,
     source_type char(1)
);

/* lookup table for power types */
create table power_type_names (
    power_name varchar(64) primary key,
    power_type char(1) not null,
    check (power_type in ('s','l','g', 'v'))
);

create table power_station (
    station_id integer primary key,
    power_name varchar(64) not null,
    area geometry(polygon, 3857)
);

create index power_station_area_idx on power_station using gist (area);

create table power_line (
    line_id integer primary key,
    power_name varchar(64) not null,
    extent    geometry(linestring, 3857),
    radius    integer array[2]
);

create index power_line_extent_idx on power_line using gist(extent);
create index power_line_startpoint_idx on power_line using gist(st_startpoint(extent));
create index power_line_endpoint_idx on power_line using gist(st_endpoint(extent));


create table power_generator (
    generator_id integer primary key,
    osm_id bigint,
    osm_type char(1),
    geometry geometry(geometry, 3857),
    location geometry(point, 3857),
    tags hstore
);

create index power_generator_location_idx on power_generator using gist(location);

-- all things recognised as power objects
insert into power_type_names (power_name, power_type)
    values ('station', 's'),
           ('substation', 's'),
           ('sub_station', 's'),
           ('plant', 's'),
           ('cable', 'l'),
           ('line', 'l'),
           ('minor_cable', 'l'),
           ('minor_line', 'l'),
           ('minor_undeground_cable', 'l'),
           ('generator', 'g'),
           ('gas generator', 'g'),
           ('wind generator', 'g'),
           ('hydro', 'g'),
           ('hydroelectric', 'g'),
           ('heliostat', 'g'),
           -- virtual elements
           ('merge', 'v'),
           ('joint', 'v');



-- we could read this out of the planet_osm_point table, but i'd
-- prefer calculating under my own control.
insert into node_geometry (node_id, point)
     select id, st_setsrid(st_makepoint(lon/100.0, lat/100.0), 3857)
       from planet_osm_nodes;

insert into way_geometry (way_id, line)
     select way_id, ST_MakeLine(n.point order by order_nr)
       from (
            select id as way_id,
                   unnest(nodes) as node_id,
                   generate_subscripts(nodes, 1) as order_nr
              from planet_osm_ways
          ) as wn
       join node_geometry n on n.node_id = wn.node_id
      group by way_id;


-- identify objects as lines or stations
insert into source_objects (osm_id, osm_type, power_id, power_type)
     select id, 'n', nextval('station_id'), 's'
       from planet_osm_nodes n
       join power_type_names t on hstore(n.tags)->'power' = t.power_name
        and t.power_type = 's';

insert into source_objects (osm_id, osm_type, power_id, power_type)
     select id, 'w', nextval('station_id'), 's'
       from planet_osm_ways w
       join power_type_names t on hstore(w.tags)->'power' = t.power_name
        and t.power_type = 's';

insert into source_objects (osm_id, osm_type, power_id, power_type)
     select id, 'w', nextval('line_id'), 'l'
       from planet_osm_ways w
       join power_type_names t on hstore(w.tags)->'power' = t.power_name
        and t.power_type = 'l';



insert into power_generator (generator_id, osm_id, osm_type, geometry, location, tags)
     select nextval('generator_id'), id, 'n', ng.point, ng.point, hstore(n.tags)
       from planet_osm_nodes n
       join node_geometry ng on ng.node_id = n.id
       join power_type_names t on hstore(tags)->'power' = t.power_name
        and t.power_type = 'g';

insert into power_generator (generator_id, osm_id, osm_type, geometry, location, tags)
     select nextval('generator_id'), id, 'w',
            case when st_isclosed(wg.line) then st_makepolygon(wg.line)
                 else wg.line end,
            st_centroid(wg.line), hstore(w.tags)
       from planet_osm_ways w
       join way_geometry wg on wg.way_id = w.id
       join power_type_names t on hstore(tags)->'power' = t.power_name
        and t.power_type = 'g';

insert into station_polygon (station_id, polygon)
     select station_id, polygon
       from (
            select o.power_id,
                   case when st_isclosed(wg.line) and st_numpoints(wg.line) > 3 then st_makepolygon(wg.line)
                        when st_numpoints(wg.line) >= 3
                          -- looks like an unclosed polygon based on endpoints distance
                         and st_distance(st_startpoint(wg.line), st_endpoint(wg.line)) < (st_length(wg.line) / 2)
                        then st_makepolygon(st_addpoint(wg.line, st_startpoint(wg.line)))
                        else null end
              from source_objects o
              join way_geometry wg on o.osm_id = wg.way_id
             where o.power_type = 's' and o.osm_type = 'w'
          ) _g(station_id, polygon)
         -- even so not all polygons will be valid
      where polygon is not null and st_isvalid(polygon);


insert into power_station (station_id, power_name, area)
     select o.power_id, hstore(n.tags)->'power', st_buffer(ng.point, :station_buffer/2)
       from source_objects o
       join planet_osm_nodes n on n.id = o.osm_id
       join node_geometry ng   on ng.node_id = o.osm_id
      where o.power_type = 's' and o.osm_type = 'n';

insert into power_station (station_id, power_name, area)
     select power_id, hstore(w.tags)->'power',
            case when sp.polygon is not null
                 then st_buffer(sp.polygon, least(:station_buffer, sqrt(st_area(sp.polygon))))
                 else st_buffer(wg.line, least(:station_buffer, st_length(wg.line)/2)) end
                  -- not sure if that is the right way to deal with line-geometry stations
       from source_objects o
       join planet_osm_ways w on w.id = o.osm_id
       join way_geometry wg on wg.way_id = o.osm_id
  left join station_polygon sp on sp.station_id = o.power_id
      where o.osm_type = 'w' and o.power_type = 's';

insert into power_line (line_id, power_name, extent, radius)
     select o.power_id, hstore(w.tags)->'power', wg.line,
            array_fill(least(:terminal_radius, st_length(wg.line)/3), array[2]) -- default radius
       from source_objects o
       join planet_osm_ways w on w.id = o.osm_id
       join way_geometry wg on wg.way_id = o.osm_id
      where o.power_type = 'l';


insert into source_tags (power_id, power_type, tags)
     select o.power_id, o.power_type, hstore(n.tags)
       from planet_osm_nodes n
       join source_objects o on o.osm_id = n.id and o.osm_type = 'n';

insert into source_tags (power_id, power_type, tags)
     select o.power_id, o.power_type, hstore(w.tags)
       from planet_osm_ways w
       join source_objects o on o.osm_id = w.id and o.osm_type = 'w';

commit;
