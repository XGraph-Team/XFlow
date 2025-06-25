begin;
drop sequence if exists network_bus_id;
drop table if exists station_transformer;
drop table if exists station_terminal;

drop table if exists network_link;
drop table if exists network_transformer;
drop table if exists network_generator;
drop table if exists network_bus;

-- split stations into busses
-- insert transformers
-- export to text format
create table station_terminal (
    station_id     integer not null,
    voltage        integer null,
    dc             boolean not null,
    network_bus_id integer primary key
);

create index station_terminal_idx on station_terminal (station_id, voltage, dc);

create table station_transformer (
    transformer_id integer primary key,
    station_id     integer,
    src_bus_id     integer references station_terminal (network_bus_id),
    dst_bus_id     integer references station_terminal (network_bus_id),
    src_voltage    integer,
    dst_voltage    integer,
    src_dc         boolean,
    dst_dc         boolean
);

create sequence network_bus_id;

with connected_line_structures as (
    select distinct station_id, voltage, dc_line
      from topology_nodes n
      join line_structure l on l.line_id = any(n.line_id)
     order by station_id, voltage
)
insert into station_terminal (station_id, voltage, dc, network_bus_id)
     select station_id, voltage, dc_line, nextval('network_bus_id')
       from connected_line_structures;

with terminal_bridges (station_id, src_bus_id, dst_bus_id, src_voltage, dst_voltage, src_dc, dst_dc) as (
    select distinct s.station_id, s.network_bus_id, d.network_bus_id, s.voltage, d.voltage, s.dc, d.dc
      from station_terminal s
      join station_terminal d on s.station_id = d.station_id and s.network_bus_id < d.network_bus_id
      join topology_nodes n on s.station_id = n.station_id
     where n.topology_name != 'joint'
)
insert into station_transformer (transformer_id, station_id, src_bus_id, dst_bus_id, src_voltage, dst_voltage, src_dc, dst_dc)
     select nextval('line_id'), station_id,
            src_bus_id, dst_bus_id,
            src_voltage, dst_voltage,
            src_dc, dst_dc
       from terminal_bridges b;


-- exported entities
create table network_bus (
    bus_id      integer primary key,
    station_id  integer,
    voltage     integer,
    dc          boolean,
    symbol      text,
    under_construction boolean,
    tags      hstore,
    geometry  text
);

create table network_link (
   link_id    integer primary key,
   src_bus_id integer references network_bus (bus_id),
   dst_bus_id integer references network_bus (bus_id),
   voltage    integer,
   circuits   integer not null,
   dc         boolean not null,
   underground boolean not null,
   under_construction boolean not null,
   length_m   numeric,
   tags       hstore,
   geometry   text
);

create table network_generator (
    generator_id integer primary key,
    bus_id       integer not null references network_bus(bus_id),
    symbol       text,
    capacity     numeric,
    tags         hstore,
    geometry     text
);

create table network_transformer (
    transformer_id integer primary key,
    symbol         text,
    src_bus_id     integer references network_bus(bus_id),
    dst_bus_id     integer references network_bus(bus_id),
    src_voltage    integer,
    dst_voltage    integer,
    src_dc         boolean,
    dst_dc         boolean,
    geometry       text
);

insert into network_bus (bus_id, station_id, voltage, dc, symbol, under_construction, tags, geometry)
     select t.network_bus_id, t.station_id, t.voltage, t.dc, n.topology_name, p.under_construction,
            p.tags, st_astext(st_transform(n.station_location, 4326))
       from topology_nodes n
       join station_terminal t on t.station_id = n.station_id
  left join station_properties p on p.station_id = n.station_id;

insert into network_link (link_id, src_bus_id, dst_bus_id, voltage, circuits, dc, underground, under_construction, length_m, tags, geometry)
     select e.line_id, s.network_bus_id, d.network_bus_id,
            l.voltage, l.circuits, l.dc_line, l.underground, l.under_construction,
            st_length(st_transform(e.line_extent, 4326)::geography), l.tags,
            st_astext(st_transform(e.line_extent, 4326))
       from topology_edges e
       join line_structure l   on l.line_id = e.line_id
       join station_terminal s on s.station_id = e.station_id[1]
        and (s.voltage = l.voltage or s.voltage is null and l.voltage is null)
        and s.dc = l.dc_line
       join station_terminal d on d.station_id = e.station_id[2]
        and (d.voltage = l.voltage or s.voltage is null
        and l.voltage is null) and d.dc = l.dc_line;

insert into network_generator (generator_id, bus_id, symbol, capacity, tags, geometry)
     select g.generator_id,
            (select network_bus_id from station_terminal t
              where g.station_id = t.station_id order by voltage asc limit 1),
            p.tags->'symbol', (p.tags->'mw')::numeric, p.tags - array['symbol','mw'],
            st_astext(st_transform(p.location, 4326))
       from topology_generators g
       join power_generator p on p.generator_id = g.generator_id;

insert into network_transformer (transformer_id, symbol, src_bus_id, dst_bus_id, src_voltage, dst_voltage, src_dc, dst_dc, geometry)
     select t.transformer_id,
            case when t.src_dc = t.dst_dc then 'transformer' else 'ac/dc' end,
            t.src_bus_id, t.dst_bus_id, t.src_voltage, t.dst_voltage, t.src_dc, t.dst_dc,
            st_astext(st_transform(n.station_location, 4326))
       from station_transformer t
       join topology_nodes n
         on t.station_id = n.station_id;

commit;
