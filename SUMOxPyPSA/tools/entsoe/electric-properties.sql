begin;
-- this replaces the 'electric' series in the OSM directory, primarily
-- because the situation for ENTSO-E is drastically simpler
drop function if exists derive_line_structure(integer);
drop function if exists join_line_structure(integer, integer array);
drop function if exists merge_line_structure(integer, integer array);
drop function if exists derive_station_properties(integer);
drop function if exists merge_station_properties(integer, integer array);
drop table if exists station_properties;
drop table if exists line_structure_conflicts;
drop table if exists line_structure;


create table station_properties (
    station_id integer primary key,
    symbol     text,
    name       text,
    under_construction boolean,
    tags       hstore
);

create table line_structure (
    line_id integer primary key,
    voltage integer,
    circuits integer,
    dc_line boolean,
    underground boolean,
    under_construction boolean,
    tags hstore
);

create table line_structure_conflicts (
    line_id   integer not null,
    conflicts line_structure array
);

insert into station_properties (station_id, symbol, name, under_construction, tags)
     select power_id, properties->'symbol', properties->'name_all', (properties->'under_construction')::boolean,
            properties - array['symbol','name_all','under_construction']
       from feature_points f
       join source_objects o on o.import_id = f.import_id and o.power_type = 's';

insert into line_structure (line_id, voltage, circuits, under_construction, underground, dc_line, tags)
     select power_id,
            substring(properties->'voltagelevel' from '^[0-9]+')::int,
            (properties->'numberofcircuits')::int,
            (properties->'underconstruction')::boolean,
            (properties->'underground')::boolean,
            (properties->'current' = 'DC'),
            properties - array['voltagelevel','numberofcircuits','shape_length','underconstruction','underground','current']
       from feature_lines f
       join source_objects o on o.import_id = f.import_id and o.power_type = 'l';

create function derive_line_structure (i integer) returns line_structure as $$
declare
    s line_structure;
    d derived_objects;
begin
    select * into s from line_structure where line_id = i;
    if (s).line_id is not null
    then
        return s;
    end if;

    select * into d from derived_objects where derived_id = i and derived_type = 'l';
    if d is null
    then
        raise exception 'Cannot find derived objects for line_id %', i;
    elsif d.operation = 'split' then
        s = derive_line_structure(d.source_id[1]);
    elsif d.operation = 'join' then
        s = join_line_structure(d.derived_id, d.source_id);
    elsif d.operation = 'merge' then
        s = merge_line_structure(d.derived_id, d.source_id);
    end if;

    -- memoize the computed line structure
    insert into line_structure (line_id, voltage, circuits, dc_line, underground, under_construction)
         select i, (s).voltage, (s).circuits, (s).dc_line, (s).underground, (s).under_construction;
    return s;
end;
$$ language plpgsql;

create function join_line_structure (i integer, j integer array) returns line_structure as $$
declare
    s line_structure array;
    c integer;
begin
    s = array(select derive_line_structure(l_id) from unnest(j) f(l_id));
    c = greatest(count(distinct (e).voltage), count(distinct (e).circuits), count(distinct (e).dc_line), count(distinct (e).underground))
        from unnest(s) e;
    if c > 1
    then
        insert into line_structure_conflicts (line_id, conflicts) values (i, s);
    end if;
    return row(i, (s[1]).voltage, (s[1]).circuits, (s[1]).dc_line,
                  (s[1]).underground, (s[1]).under_construction,
                  (s[1]).tags); -- TODO merge tags
end
$$ language plpgsql;

create function merge_line_structure (i integer, j integer array) returns line_structure as $$
begin
    -- this causes some problems, may want to reconsider the spatial-first strategy
    return join_line_structure(i, j);
end;
$$ language plpgsql;

create function derive_station_properties(i integer) returns station_properties as $$
declare
    p station_properties;
    d derived_objects;
begin
    select * into p from station_properties where station_id = i;
    if (p).station_id is not null
    then
        return p;
    end if;
    select * into d from derived_objects where derived_id = i and derived_type = 's';
    if d is null
    then
        raise exception 'Cannot find derived objects for station_id %', i;
    elsif (d).operation = 'merge'
    then
        p = merge_station_properties(i, d.source_id);
    end if;
    insert into station_properties (station_id, symbol, name, under_construction, tags)
         select i, (p).symbol, (p).name, (p).under_construction, (p).tags;
    return p;
end;
$$ language plpgsql;

create function merge_station_properties(i integer, m integer array) returns station_properties as $$
begin
    -- very noppy implementation
    return derive_station_properties(s_id) from unnest(m) s_id limit 1;
end
$$ language plpgsql;

do $$
begin
    perform derive_line_structure(line_id) from topology_edges e
      where not exists (select 1 from line_structure l where l.line_id = e.line_id);
    perform derive_station_properties(station_id) from topology_nodes n
      where topology_name != 'joint'
        and not exists (select 1 from station_properties s where s.station_id = n.station_id);
end
$$ language plpgsql;
commit;
