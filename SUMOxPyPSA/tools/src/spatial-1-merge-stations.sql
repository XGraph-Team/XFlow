begin;
drop table if exists overlapping_stations;
drop table if exists station_set;
drop table if exists merged_stations;

create table overlapping_stations (
    a_id integer not null,
    b_id integer not null,
    primary key (a_id, b_id)
);

create table station_set (
   station_id integer primary key,
   set_key    integer not null
);

create index station_set_key on station_set (set_key);

create table merged_stations (
    new_id integer primary key,
    old_id integer array,
    area   geometry(polygon, 3857)
);


insert into overlapping_stations (a_id, b_id)
     select a.station_id, b.station_id
       from power_station a, power_station b
      where a.station_id < b.station_id
        and st_dwithin(a.area, b.area, 0);

insert into station_set (station_id, set_key)
    select station_id, station_id from (
         select a_id from overlapping_stations union select b_id from overlapping_stations
    ) f (station_id);

do $$
declare
    pair overlapping_stations;
    src_key integer;
    dst_key integer;
begin
    for pair in select * from overlapping_stations loop
         src_key = set_key from station_set where station_id = pair.a_id;
         dst_key = set_key from station_set where station_id = pair.b_id;
         if src_key != dst_key then
             update station_set set set_key = src_key where set_key = dst_key;
         end if;
    end loop;
end;
$$ language plpgsql;

insert into merged_stations (new_id, old_id, area)
   select nextval('station_id'), old_id, area from (
        select array_agg(z.station_id), st_union(s.area)
          from station_set z
          join power_station s on s.station_id = z.station_id
         group by set_key
   ) f(old_id, area);

-- TODO ; somehow during the union of ares, we're getting multipolygons
insert into power_station (station_id, power_name, area)
     select new_id,
            (select power_name from power_station
              where station_id = any(old_id)
              order by st_area(area) desc limit 1),
            area
       from merged_stations;

insert into derived_objects (derived_id, derived_type, operation, source_id, source_type)
     select new_id, 's', 'merge', old_id, 's'
       from merged_stations;

delete from power_station s where station_id in (
    select unnest(old_id) from merged_stations
);

commit;
