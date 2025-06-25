begin;
/* functions */
drop function if exists array_remove(anyarray, anyarray);
drop function if exists array_replace(anyarray, anyarray, anyarray);
drop function if exists array_sym_diff(anyarray, anyarray);
drop function if exists array_merge(anyarray, anyarray);

drop function if exists connect_lines(a geometry(linestring), b geometry(linestring));
drop function if exists minimal_radius(geometry, geometry, int array);


create function array_remove(a anyarray, b anyarray) returns anyarray as $$
begin
    return array((select unnest(a) except select unnest(b)));
end;
$$ language plpgsql;

create function array_replace(a anyarray, b anyarray, n anyarray) returns anyarray as $$
begin
    return array((select unnest(a) except select unnest(b) union select unnest(n)));
end;
$$ language plpgsql;

create function array_sym_diff(a anyarray, b anyarray) returns anyarray as $$
begin
    return array(((select unnest(a) union select unnest(b))
                   except
                  (select unnest(a) intersect select unnest(b))));
end;
$$ language plpgsql;

create function array_merge(a anyarray, b anyarray) returns anyarray as $$
begin
    return array(select unnest(a) union select unnest(b));
end;
$$ language plpgsql;


create function connect_lines (a geometry(linestring), b geometry(linestring)) returns geometry(linestring) as $$
begin
    -- select the shortest line that comes from joining the lines
     -- in all possible directions
    return (select e from (
                select unnest(
                         array[st_makeline(a, b),
                               st_makeline(a, st_reverse(b)),
                               st_makeline(st_reverse(a), b),
                               st_makeline(st_reverse(a), st_reverse(b))]) e) f
                order by st_length(e) limit 1);
end;
$$ language plpgsql;

create function minimal_radius(line geometry, area geometry, radius int array) returns int array as $$
begin
    return array[case when st_dwithin(st_startpoint(line), area, 1) then 1 else radius[1] end,
                 case when st_dwithin(st_endpoint(line), area, 1) then 1 else radius[2] end];
end;
$$ language plpgsql;

commit;
