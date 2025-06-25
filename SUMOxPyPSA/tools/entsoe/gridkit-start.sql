-- script to transfer features to gridkit power stations and lines
begin;
drop table if exists power_station;
drop table if exists power_line;
drop table if exists power_generator;
drop table if exists source_objects;
drop table if exists derived_objects;

drop sequence if exists station_id;
drop sequence if exists line_id;
drop sequence if exists generator_id;

create table power_station (
    station_id integer primary key,
    power_name varchar(64) not null,
    area geometry(polygon, 3857)
);

create index power_station_area on power_station using gist (area);

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
    location geometry(point, 3857),
    tags hstore
);

create index power_generator_location_idx on power_generator using gist(location);

create sequence line_id;
create sequence station_id;
create sequence generator_id;

create table source_objects (
    power_id integer not null,
    power_type char(1) not null,
    import_id integer not null,
    primary key (power_id, power_type)
);

create table derived_objects (
    derived_id integer not null,
    derived_type char(1) not null,
    operation varchar(16),
    source_id integer array,
    source_type char(1),
    primary key (derived_id, derived_type)
);

insert into source_objects (power_id, power_type, import_id)
     select nextval('station_id'), 's', import_id
       from feature_points;

insert into source_objects (power_id, power_type, import_id)
     select nextval('line_id'), 'l', import_id
       from feature_lines;

insert into power_station (station_id, power_name, area)
     select o.power_id, properties->'symbol',
            st_buffer(st_transform(point, 3857), :station_buffer)
       from feature_points f
       join source_objects o
         on o.import_id = f.import_id
      where o.power_type = 's';

insert into power_line (line_id, power_name, extent, radius)
     select o.power_id, 'line', st_transform(line, 3857),
            array[:terminal_radius,:terminal_radius]
       from feature_lines f
       join source_objects o on o.import_id = f.import_id
      where o.power_type = 'l';

insert into power_generator (generator_id, location, tags)
     select nextval('generator_id'), st_transform(point, 3857), properties
       from feature_points
      where properties->'symbol' not in (
                'Substation',
                'Substation, under construction',
                'Converter Station',
                'Converter Station, under construction',
                'Converter Station Back-to-Back'
            );

commit;
