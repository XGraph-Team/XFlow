begin;
drop table if exists isolated_hvdc_terminal;
create table isolated_hvdc_terminal (
    terminal_id integer primary key,
    terminal_location geometry(point,3857),
    station_id integer not null,
    connection_line geometry(linestring,3857)
);

insert into isolated_hvdc_terminal (terminal_id, terminal_location,
                                    station_id, connection_line)
     select t.station_id, t.station_location, f.station_id,
            st_makeline(f.station_location, t.station_location)
       from topology_nodes t
       join lateral (
            select s.station_id, n.station_location from power_station s
              join topology_nodes n on n.station_id = s.station_id
             where t.station_id != n.station_id
                -- not to another HVDC station, or to a joint
               and n.topology_name not in (
                   'joint',
                   'Wind farm',
                   'Converter Station',
                   'Converter Station Back-to-back',
                   'Converter Station, under construction'
                 )
                -- indexed k-nearest neighbor
             order by t.station_location <-> s.area limit 1
             -- TODO, this distorts lengths due to projection; maybe
             -- better results with geography measurements
          ) f on st_distance(t.station_location, f.station_location) < :hvdc_distance
      where t.topology_name in (
                'Converter Station',
                'Converter Station Back-to-back',
                'Converter Station, under construction'
            )
         -- all lines are hvdc lines
        and not exists (
            select 1 from line_structure l
             where l.line_id = any(t.line_id) and not l.dc_line
          );

insert into network_transformer (transformer_id, symbol, src_bus_id,  dst_bus_id,
                                 src_voltage, dst_voltage, src_dc, dst_dc, geometry)
      select nextval('line_id'), 'ac/dc',  c.bus_id, s.bus_id,
             c.voltage, s.voltage, c.dc, s.dc,
             st_astext(st_transform(i.connection_line, 4326))
        from isolated_hvdc_terminal i
        join network_bus c on c.station_id = i.terminal_id
        join network_bus s on s.station_id = i.station_id;
-- TODO, maybe join lateral to find only the highest voltage / best matching bus

commit;
