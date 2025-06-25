begin;
drop function if exists fair_division(n int, d int);
drop function if exists array_mult(n int array, int);

create function fair_division (n int, d int) returns int array as $$
begin
    return array_cat(array_fill( n / d + 1, array[n % d]), array_fill( n / d, array[d - n % d]));
end;
$$ language plpgsql;

create function array_mult(n int array, x int) returns int array as $$
begin
    return array(select v*x from unnest(n) v);
end;
$$ language plpgsql;

-- use the 'circuits' tag to compute the cables if this is not set
update line_tags set cables = array_mult(circuits, 3)
 where cables is null and circuits is not null;

drop table if exists divisible_cables;
create table divisible_cables (
    line_id integer primary key,
    num_lines integer,
    total_cables integer,
    cables integer array
);

insert into divisible_cables (line_id, num_lines, total_cables)
     select line_id, case when array_length(voltage, 1) > 1 then array_length(voltage, 1)
                          else array_length(frequency, 1) end, cables[1]
       from line_tags l
      where (array_length(voltage, 1) > 1 or array_length(frequency, 1) > 1) and array_length(cables, 1) = 1
        and cables[1] > 4;


update divisible_cables
   set cables = case when total_cables >= num_lines * 3 and total_cables % 3 = 0 then array_mult(fair_division(total_cables / 3, num_lines), 3)
                     when total_cables >= num_lines * 4 and total_cables % 4 = 0 then array_mult(fair_division(total_cables / 4, num_lines), 4)
                     when total_cables >= 7 and (total_cables - 4) % 3 = 0 then array_cat(array[4],  array_mult(fair_division((total_cables - 4) / 3, num_lines - 1), 3))
                     when total_cables >= 11 and (total_cables - 8) % 3 = 0 then array_cat(array[8], array_mult(fair_division((total_cables - 8) / 3, num_lines-1), 3))
                     else array[total_cables] end;

-- can't seem to solve this one analytically...
update divisible_cables set cables = array[4,4,3] where total_cables = 11 and num_lines = 3;

update line_tags t set cables = d.cables from divisible_cables d where d.line_id = t.line_id;

-- fix 16.67 Hz to 16.7 frequency for consistency.
update line_tags
   set frequency = array_replace(frequency::numeric[],16.67,16.7)
 where 16.67 = any(frequency);

-- fix inconsistently striped lines

drop table if exists inconsistent_line_tags;
create table inconsistent_line_tags (
    line_id integer primary key,
    voltage integer array,
    frequency float array,
    cables integer array,
    wires integer array
);

-- this affects surprisingly few lines, actually
insert into inconsistent_line_tags (line_id, voltage, frequency, cables, wires)
     select line_id, voltage, frequency, cables, wires
       from line_tags t
      where num_classes > 2 and
            array_length(voltage, 1) between 2 and num_classes - 1 or
            array_length(frequency, 1) between 2 and num_classes - 1 or
            array_length(cables, 1) between 2 and num_classes - 1 or
            array_length(wires, 1) between 2 and num_classes - 1;

-- patch cables and wires
-- default cables is 3, default wires is 1
update inconsistent_line_tags set cables = array_cat(cables, array_fill(null::int, array[array_length(voltage, 1) - array_length(cables, 1)]))
    where array_length(voltage, 1) > array_length(cables, 1) and array_length(cables, 1) > 1;

update inconsistent_line_tags set wires = array_cat(wires, array_fill(null::int, array[array_length(voltage,1) - array_length(wires, 1)]))
    where array_length(voltage, 1) > array_length(wires, 1) and array_length(wires, 1) > 1;

update inconsistent_line_tags set frequency = array_cat(frequency, array_fill(null::float, array[array_length(voltage, 1) - array_length(frequency, 1)]))
    where array_length(voltage, 1) > array_length(frequency, 1) and array_length(frequency, 1) > 1;

-- peel of excess wires
update inconsistent_line_tags set wires = wires[1:(array_length(voltage,1))]
    where array_length(wires, 1) > array_length(voltage, 1) and array_length(voltage, 1) > 1;

-- that's enough! for now at least
update line_tags l
   set frequency = i.frequency, cables = i.cables, wires = i.wires,
       num_classes = greatest(array_length(i.voltage, 1), array_length(i.frequency, 1),
                              array_length(i.cables, 1), array_length(i.wires, 1))
  from inconsistent_line_tags i
 where l.line_id = i.line_id;

commit;
