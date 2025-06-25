begin;
/* temporarily create the table so that the line structure type exists */
create table if not exists line_structure ( line_id integer );
drop function if exists derive_line_structure(integer);
drop function if exists join_line_structure(integer, integer array);
drop function if exists merge_line_structure(integer, integer array);
drop function if exists line_structure_majority(integer, line_structure array, boolean);
drop function if exists line_structure_distance(line_structure, line_structure);
drop function if exists line_structure_classify(integer, line_structure array, integer);
drop function if exists line_structure_set(integer, line_structure array);
drop table if exists line_structure;

create table line_structure (
    line_id integer,
    part_nr integer,
    -- properties
    voltage integer,
    frequency float,
    cables integer,
    wires integer,
    -- counts
    num_objects integer,
    num_conflicts integer array[4],
    num_classes integer,
    primary key (line_id, part_nr)
);


create function derive_line_structure (i integer) returns line_structure array as $$
declare
    r line_structure array;
    d derived_objects;
begin
     r = array(select row(l.*) from line_structure l where line_id = i);
     if array_length(r, 1) is not null then
         return r;
     end if;
     select * into d from derived_objects where derived_id = i and derived_type = 'l';
     if d.derived_id is null then
         raise exception 'No derived object for line_id %', i;
     elsif d.operation = 'join' then
         r = join_line_structure(i, d.source_id);
     elsif d.operation = 'merge' then
         r = merge_line_structure(i, d.source_id);
     elsif d.operation = 'split' then
         r = derive_line_structure(d.source_id[1]);
     end if;
     if array_length(r, 1) is null then
         raise exception 'Could not derive line_structure for %', i;
     end if;
     -- store and return
     insert into line_structure (line_id, part_nr, voltage, frequency, cables, wires, num_objects, num_conflicts, num_classes)
          select * from line_structure_set(i, r);
     return array(select row(l.*) from line_structure_set(i, r) l);
end;
$$ language plpgsql;

create function line_structure_set(i integer, r line_structure array) returns setof line_structure as $$
begin
     return query select i, s, (l).voltage, (l).frequency, (l).cables, (l).wires, (l).num_objects, (l).num_conflicts, (l).num_classes
                    from (select unnest(r), generate_subscripts(r, 1)) f(l, s);
end;
$$ language plpgsql;

create function join_line_structure(i integer, j integer array) returns line_structure array as $$
declare
    r line_structure array;
    n integer;
begin
    r = array(select unnest(derive_line_structure(line_id)) from unnest(j) line_id);
    n = max((e).num_classes) from unnest(r) as e;
    if n > 1 then
       return array(select line_structure_majority(i, array_agg(l), false)
                      from line_structure_classify(i, r, n) c
                      join unnest(r) l on (l).line_id = c.source_id and (l).part_nr = c.part_nr
                     group by c.class_key);
    else
        return array[line_structure_majority(i, r, false)];
    end if;
end;
$$ language plpgsql;


create function merge_line_structure(i integer, j integer array) returns line_structure array as $$
declare
    r line_structure array;
    n integer;
begin
    r = array(select unnest(derive_line_structure(line_id)) from unnest(j) line_id);
    -- if we have multiple classes, multiple voltages, or frequencies, choose to treat them as s
    n = greatest(max((e).num_classes::bigint), count(distinct (e).voltage), count(distinct (e).frequency)) from unnest(r) as e;
    if n > 1 then
        -- divide over c classes
        return array(select line_structure_majority(i, array_agg(l), true)
                       from line_structure_classify(i, r, n) c
                       join unnest(r) l on (l).line_id = c.source_id and (l).part_nr = c.part_nr
                      group by c.class_key);
    else
        return array[line_structure_majority(i, r, true)];
    end if;
end;
$$ language plpgsql;

create function line_structure_majority(i integer, d line_structure array, sum_cables boolean) returns line_structure as $$
declare
    r line_structure;
begin
    with raw_data (line_id, part_nr, voltage, frequency, cables, wires, num_objects, num_conflicts, num_classes) as (
        select (e).* from unnest(d) e
    ),
    cnt_t (n) as ( select sum(num_objects) from raw_data ),
    cnt_v (n) as ( select sum(num_objects) from raw_data where voltage is not null ),
    cnt_f (n) as ( select sum(num_objects) from raw_data where frequency is not null ),
    cnt_c (n) as ( select sum(num_objects) from raw_data where cables is not null ),
    cnt_w (n) as ( select sum(num_objects) from raw_data where wires is not null ),
    num_c (n) as ( select max(num_classes) from raw_data ),
    vlt(voltage, conflicts) as (
        select voltage, coalesce(n - score, 0) from (
             select voltage, sum(num_objects) - sum(num_conflicts[1])
               from raw_data
              group by voltage
        ) _t (voltage, score), cnt_v
        order by voltage is not null desc, score desc, voltage asc limit 1
    ),
    frq(frequency, conflicts) as (
        select frequency, coalesce(n - score, 0) from (
             select frequency, sum(num_objects) - sum(num_conflicts[2])
               from raw_data
              group by frequency
        ) _t (frequency, score), cnt_f
        order by frequency is not null desc, score desc, frequency asc limit 1
    ),
    cbl(cables, conflicts) as (
        select cables, coalesce(n - score, 0) from (
             select cables, sum(num_objects) - sum(num_conflicts[3])
               from raw_data
              group by cables
        ) _t (cables, score), cnt_c
        order by cables is not null desc, score desc, cables asc limit 1
    ),
    wrs(wires, conflicts) as (
        select wires, coalesce(n - score, 0) from (
             select wires, sum(num_objects) - sum(num_conflicts[4])
               from raw_data
              group by wires
        ) _t (wires, score), cnt_w
        order by wires is not null desc, score desc, wires asc limit 1
    ),
    _sum (cables) as (
        select sum(cables) from raw_data where cables is not null
    )
    select null, null, vlt.voltage, frq.frequency,
           case when sum_cables then _sum.cables else cbl.cables end,
           wrs.wires, cnt_t.n,
           array[vlt.conflicts, frq.conflicts, cbl.conflicts, wrs.conflicts],
           num_c.n
      into r
      from vlt, frq, cbl, wrs, cnt_t, num_c, _sum;
    return r;
end;
$$ language plpgsql;


create function line_structure_distance(a line_structure, b line_structure) returns numeric as $$
begin
    return case when a.voltage is null or b.voltage is null then 1
                when a.voltage = b.voltage then 0
                when least(a.voltage, b.voltage) = 0 then 4
                else 2*greatest(a.voltage, b.voltage)::float / least(a.voltage, b.voltage)::float end
                +
           case when a.frequency is null or b.frequency is null then 1
                when a.frequency = b.frequency then 0
                when least(a.frequency, b.frequency) = 0 then 4
                else 2*greatest(a.frequency, b.frequency) / least(a.frequency, b.frequency) end
                +
           case when a.cables is null or b.cables is null then 1
                when a.cables = b.cables then 0
                when least(a.cables, b.cables) = 0 then 2
                else 0.7*greatest(a.cables, b.cables)::float / least(a.cables, b.cables)::float end
                +
           case when a.wires is null or b.wires is null then 1
                when a.wires = b.wires then 0
                when least(a.wires, b.wires) = 0 then 2
                else 0.7*greatest(a.wires, b.wires)::float / least(a.wires, b.wires)::float end;
end;
$$ language plpgsql;



-- TODO this needs a structure_id of sorts... (OR we can introduce link_id here, but that means we need two tables)
drop table if exists line_structure_class;
create table line_structure_class (
    line_id integer,
    source_id integer,
    part_nr   integer,
    class_key integer,
    primary key (line_id, source_id, part_nr)
);

create index line_structure_class_key_idx
          on line_structure_class (line_id, class_key);

create function line_structure_classify (i integer, r line_structure array, n integer) returns setof line_structure_class as $$
declare
    edge record;
    src_key integer;
    dst_key integer;
    num_edges integer;
begin
    num_edges  = 0;
    insert into line_structure_class (line_id, source_id, part_nr, class_key)
         select i, (unnest(r)).line_id, (unnest(r)).part_nr, generate_subscripts(r, 1);

    for edge in with pairs (src_id, src_pt, dst_id, dst_pt, cost) as (
        select a_id, a_pt, b_id, b_pt, line_structure_distance(_s, _t)
          from unnest(r) _s(a_id, a_pt),
               unnest(r) _t(b_id, b_pt) -- line id is the first column
         where a_id < b_id
      order by line_structure_distance(_s, _t) asc
    ) select * from pairs loop
        src_key := class_key from line_structure_class
                            where line_id = i
                              and source_id = edge.src_id
                              and part_nr = edge.src_pt;
        dst_key := class_key from line_structure_class
                            where line_id = i
                              and source_id = edge.dst_id
                              and part_nr = edge.dst_pt;
        if src_key = dst_key then
            continue;
        elsif num_edges + n = array_length(r, 1) then
            exit;
        else
            update line_structure_class
               set class_key = least(src_key, dst_key)
             where line_id = i
               and class_key = greatest(src_key, dst_key);
            num_edges = num_edges + 1;
        end if;
    end loop;
    return query select line_id, source_id, part_nr, class_key
                   from line_structure_class
                  where line_id = i;
end;
$$ language plpgsql;


insert into line_structure (line_id, part_nr, voltage, frequency, cables, wires, num_objects, num_conflicts, num_classes)
     select line_id, generate_series(1, num_classes),
            case when voltage is not null then unnest(voltage) end,
            case when frequency is not null then unnest(frequency) end,
            case when cables is not null then unnest(cables) end,
            case when wires is not null then unnest(wires) end,
            1, array[0,0,0,0], num_classes
       from line_tags;


do $$
declare
    i integer;
    c integer;
begin
    -- todo, we may want to split this into partial queries, because
    -- a single run takes a /very/ long time...
    i = 0;
    loop
        c = count(*) from topology_edges e where not exists (
             select 1 from line_structure l where l.line_id = e.line_id
        );
        i := i + 1;
        exit when c = 0;
        raise notice 'Iteration %, % left', i, c;

        perform derive_line_structure(derived_id)
           from derived_objects j
           join topology_edges e on e.line_id = j.derived_id
          where derived_type = 'l'
            and not exists (select 1 from line_structure l where l.line_id = e.line_id)
          order by line_id asc
         limit 1000;
    end loop;
end;
$$ language plpgsql;

commit;
