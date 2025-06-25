begin;
drop table if exists network_links;
drop table if exists network_buses;
drop table if exists network_generators;
drop table if exists network_transformers;
drop sequence if exists link_id;
drop sequence if exists bus_id;
create sequence link_id;
create sequence bus_id;



create table network_bus (
    bus_id integer primary key,
    station_id integer not null,
    voltage integer,
    frequency numeric,
    station_name text,
    station_operator text,
    substation text,
    geometry text
);

create table network_link (
    link_id integer primary key,
    line_id integer not null,
    part_nr integer not null,
    voltage integer,
    frequency numeric,
    cables integer,
    wires integer,
    geometry text
);

-- a trasnforer is a link, but not like the others
create table network_transformer (
    transformer_id integer primary key,
    station_id     integer,
    src_bus_id     integer references network_bus (bus_id),
    dst_bus_id     integer references network_bus (bus_id),
    src_voltage    integer,
    dst_voltage    integer,
    src_frequency  numeric,
    dst_frequency  numeric,
    geometry       text
);

create table network_generator (
    generator_id integer primary key,
    tags hstore,
    geometry text
)

commit;
