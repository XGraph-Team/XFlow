begin;
drop table if exists intersecting_terminals;
drop table if exists terminal_sets;
drop sequence if exists terminal_set_keys;
create sequence terminal_set_keys;

create table intersecting_terminals (
   src_id integer not null,
   src_pt integer not null,
   dst_id integer not null,
   dst_pt integer not null
);

-- sets of mutually intersecting terminals
create table terminal_sets (
   line_id integer not null,
   line_pt integer not null,
   set_key integer not null,
   primary key (line_id, line_pt)
);

create index terminal_sets_key on terminal_sets (set_key);

insert into intersecting_terminals (src_id, src_pt, dst_id, dst_pt)
     select a.line_id, 1, b.line_id, 1 from power_line a, power_line b
      where a.line_id != b.line_id and st_dwithin(st_startpoint(a.extent), st_startpoint(b.extent), a.radius[1])
        and not exists (select 1 from power_station s where st_dwithin(s.area, st_startpoint(a.extent), a.radius[1]));

insert into intersecting_terminals (src_id, src_pt, dst_id, dst_pt)
     select a.line_id, st_numpoints(a.extent), b.line_id, 1 from power_line a, power_line b
      where a.line_id != b.line_id and st_dwithin(st_endpoint(a.extent), st_startpoint(b.extent), a.radius[2])
        and not exists (select 1 from power_station s where st_dwithin(s.area, st_endpoint(a.extent), a.radius[2]));

insert into intersecting_terminals (src_id, src_pt, dst_id, dst_pt)
     select a.line_id, st_numpoints(a.extent), b.line_id, st_numpoints(b.extent) from power_line a, power_line b
      where a.line_id != b.line_id and st_dwithin(st_endpoint(a.extent), st_endpoint(b.extent), a.radius[2])
        and not exists (select 1 from power_station s where st_dwithin(s.area, st_endpoint(a.extent), a.radius[2]));

insert into terminal_sets (line_id, line_pt, set_key)
    select line_id, line_pt, nextval('terminal_set_keys')
       from (
            select src_id, src_pt from intersecting_terminals
            union
            select dst_id, dst_pt from intersecting_terminals
       ) f (line_id, line_pt);

do $$
declare
    i intersecting_terminals;
    s int;
    d int;
begin
    for i in select * from intersecting_terminals loop
        s = set_key from terminal_sets where line_id = i.src_id and line_pt = i.src_pt;
        d = set_key from terminal_sets where line_id = i.dst_id and line_pt = i.dst_pt;
        if s != d then
            update terminal_sets set set_key = least(s,d) where set_key = greatest(s,d);
        end if;
    end loop;
end
$$ language plpgsql;

commit;
