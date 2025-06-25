begin;
drop table if exists high_voltage_lines;
drop table if exists high_voltage_stations;
create table high_voltage_lines (
    line_id integer primary key,
    line_extent geometry(linestring,3857) -- for visualization
);
create table high_voltage_stations (
    station_id integer primary key,
    station_location geometry(point, 3857)
);

-- because we've added the line voltage to the station structure in
-- the previous step, we don't need to check lines to find nodes anymore
insert into high_voltage_stations (station_id, station_location)
     select n.station_id, n.station_location
       from topology_nodes n
       join station_structure s on n.station_id = s.station_id
      where 220000 <= any(s.voltage)
        and (not 16.7 = all(s.frequency) or array_length(s.frequency,1) is null);


-- we do need to repeat the station check, otherwise it isn't
-- sensitive enough (NULLs are ok, exclusion values are not)
insert into high_voltage_lines (line_id, line_extent)
     select e.line_id, line_extent
       from topology_edges e
       join line_structure l on l.line_id = e.line_id
      where l.voltage >= 220000 and (l.frequency != 16.7 or l.frequency is null)

      union

     select e.line_id, line_extent
       from topology_edges e
       join station_structure a on a.station_id = e.station_id[1]
       join station_structure b on b.station_id = e.station_id[2]
      where (not 220000 >= all(a.voltage) or array_length(a.voltage, 1) is null)
        and (not 220000 >= all(b.voltage) or array_length(b.voltage, 1) is null)
        and (not 16.7 = all(a.frequency) or array_length(a.frequency, 1) is null)
        and (not 16.7 = all(b.frequency) or array_length(b.frequency, 1) is null)
        and ( 220000 <= any(a.voltage) or 220000 <= any(b.voltage) );

-- but we can have added lines to stations not in the high-voltage
-- set, and that is not good
insert into high_voltage_stations (station_id, station_location)
     select station_id, station_location
       from topology_nodes n
      where exists (
            select 1 from high_voltage_lines h
             where h.line_id = any(n.line_id)
          )
        and not exists (
            select 1 from high_voltage_stations h
             where h.station_id = n.station_id
          );
commit;
