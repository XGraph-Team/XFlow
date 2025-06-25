begin;
drop table if exists line_tags;
drop table if exists station_tags;
drop table if exists wires_to_numbers;
drop function if exists string_to_integer_array(text,text);
drop function if exists string_to_float_array(text,text);
drop function if exists number_of_wires(text);


-- table of parsed line tags
create table line_tags (
    line_id integer primary key,
    power_name varchar(64) not null,
    voltage integer array,
    frequency float array,
    cables integer array,
    wires integer array,
    circuits integer array,
    num_classes integer
);

create table station_tags (
    station_id integer primary key,
    power_name varchar(64) not null,
    -- we don't /really/ care about those, since they can be derived
    -- from connected lines
    voltage integer array,
    frequency float array,
    station_name text,
    station_operator text,
    substation text
);


create function string_to_integer_array(a text, b text) returns integer array as $$
declare
    r integer array;
    t text;
begin
    for t in select unnest(string_to_array(a, b)) loop
        begin
            r = r || t::int;
        exception when others then
            r = r || null;
        end;
    end loop;
    return r;
end;
$$ language plpgsql;

create function string_to_float_array(a text, b text) returns float array as $$
declare
    r float array;
    t text;
begin
    for t in select unnest(string_to_array(a, b)) loop
        begin
            r = r || t::float;
        exception when others then
            r = r || null;
        end;
    end loop;
    return r;
end;
$$ language plpgsql;


create table wires_to_numbers (
    name varchar(16),
    nr   integer
);

insert into wires_to_numbers(name, nr)
    values ('single', 1),
           ('double', 2),
           ('triple', 3),
           ('quad', 4);


create function number_of_wires(a text) returns integer array as $$
declare
    r integer array;
    t text;
    w wires_to_numbers;
begin
    for t in select unnest(string_to_array(a, ';')) loop
        select * into w from wires_to_numbers where name = t;
        if w is not null
        then
             r = r || w.nr;
        else
            begin
                r = r || t::integer;
            exception when others then
                r = r || null;
            end;
        end if;
    end loop;
    return r;
end;
$$ language plpgsql;


insert into line_tags (line_id, power_name, voltage, frequency, cables, wires, circuits)
     select power_id, tags->'power',
            string_to_integer_array(tags->'voltage',';'),
            string_to_float_array(tags->'frequency',';'),
            string_to_integer_array(tags->'cables',';'),
            number_of_wires(tags->'wires'),
            string_to_integer_array(tags->'circuits',';')
       from source_tags
      where power_type = 'l';

-- compute num_classes
update line_tags
   set num_classes = greatest(array_length(voltage, 1), array_length(frequency, 1),
                              array_length(cables, 1), array_length(wires, 1),
                              array_length(circuits, 1), 1);

insert into station_tags (station_id, power_name, voltage, frequency, station_name, station_operator, substation)
     select power_id, tags->'power',
            string_to_integer_array(tags->'voltage', ';'),
            string_to_float_array(tags->'frequency',';'),
            tags->'name', tags->'operator', tags->'substation'
       from source_tags
      where power_type = 's';

commit;
