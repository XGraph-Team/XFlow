begin;
drop table if exists line_pairs;
drop table if exists line_sets;
drop table if exists merged_lines;

-- outer radius of merged line
drop function if exists outer_radius(geometry, int array, geometry, int array, geometry);
create function outer_radius (a_e geometry, a_r int array, b_e geometry, b_r int array, c_e geometry) returns int array as $$
begin
    return array[case when st_startpoint(a_e) = st_startpoint(c_e) then a_r[1]
                      when st_endpoint(a_e)   = st_startpoint(c_e) then a_r[2]
                      when st_startpoint(b_e) = st_startpoint(c_e) then b_r[1]
                      when st_endpoint(b_e)   = st_startpoint(c_e) then b_r[2] end,
                 case when st_startpoint(a_e) = st_endpoint(c_e) then a_r[1]
                      when st_endpoint(a_e)   = st_endpoint(c_e) then a_r[2]
                      when st_startpoint(b_e) = st_endpoint(c_e) then b_r[1]
                      when st_endpoint(b_e)   = st_endpoint(c_e) then b_r[2] end];
end;
$$ language plpgsql;

create table line_pairs (
    src_id integer,
    dst_id integer,
    primary key (src_id, dst_id)
);

create table line_sets (
    set_key integer not null,
    line_id integer primary key,
    extent  geometry(linestring, 3857),
    radius  integer array[2]
);


create table merged_lines (
    new_id  integer primary key,
    old_id  integer array,
    extent  geometry(linestring, 3857),
    radius  integer array[2]
);

insert into line_pairs (src_id, dst_id)
    select distinct min(line_id), max(line_id)
        from terminal_sets
        group by set_key having count(*) = 2;

insert into line_sets (set_key, line_id, extent, radius)
    select line_id, line_id, extent, radius from power_line
        where line_id in (
           select src_id from line_pairs union select dst_id from line_pairs
        );


create index line_sets_k on line_sets (set_key);
-- union-find algorithm again.

do $$
declare
    src line_sets;
    dst line_sets;
    pair line_pairs;
    ext geometry(linestring,3857);
    rad int array[2];
begin
    for pair in select * from line_pairs loop
        select * into src from line_sets where line_id = pair.src_id;
        select * into dst from line_sets where line_id = pair.dst_id;
        if src.set_key != dst.set_key then
            update line_sets set set_key = src.set_key where set_key = dst.set_key;
            ext = connect_lines(src.extent, dst.extent);
            rad = outer_radius(src.extent, src.radius, dst.extent, dst.radius, ext);
            update line_sets set extent = ext, radius = rad where set_key = src.set_key;
        end if;
     end loop;
end
$$ language plpgsql;

insert into merged_lines (new_id, extent, radius, old_id)
    select nextval('line_id'), extent, radius, array(select z.line_id from line_sets z where z.set_key = s.set_key)
        from line_sets s where line_id = set_key;

insert into power_line (line_id, power_name, extent, radius)
    select new_id, 'merge', extent, radius from merged_lines;

insert into derived_objects (derived_id, derived_type, operation, source_id, source_type)
     select new_id, 'l', 'join', old_id, 'l'
       from merged_lines;


delete from power_line l where line_id in (
    select unnest(old_id) from merged_lines m
);

commit;
