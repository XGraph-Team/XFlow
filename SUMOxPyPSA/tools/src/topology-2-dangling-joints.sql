begin;
drop table if exists removed_nodes;
drop table if exists removed_edges;

create table removed_nodes (
    station_id integer primary key,
    location geometry(point, 3857)
);

create table removed_edges (
    line_id integer primary key,
    extent  geometry(linestring, 3857)
);



-- iteratively prune 'dangling' joints, a joint should attach at least two stations
do $$
declare
   last_count integer;
   new_count integer;
begin
   last_count = 0;
   loop
       insert into removed_nodes (station_id, location)
              select n.station_id, n.station_location
                     from topology_nodes n
                     join topology_edges e on e.line_id = any(n.line_id)
                     join topology_nodes c on c.station_id = any(e.station_id)
                     where c.station_id != n.station_id
                       and n.topology_name = 'joint'
                     group by n.station_id having count(distinct c.station_id) < 2;
       new_count = count(*) from removed_nodes;
       raise notice 'found %', new_count - last_count;
       if new_count = last_count
       then
           raise notice 'total %', last_count;
           exit;
       end if;
       last_count = new_count;
       delete from topology_nodes
           where station_id in (select station_id from removed_nodes);
    end loop;
end;
$$ language plpgsql;


-- we're going to remove edges, and finally nodes
insert into removed_edges (line_id, extent)
     select line_id, line_extent from topology_edges where line_id in (
         select line_id from (
             select line_id, unnest(station_id)
         ) f(line_id, station_id) where station_id not in (
             select station_id from topology_nodes
         )
    );

delete from topology_edges where line_id in (select line_id from removed_edges);

update topology_nodes n set line_id = array_remove(n.line_id, r.line_id)
    from (
        select station_id, array_agg(line_id) from (
            select station_id, unnest(line_id) from topology_nodes
        ) f(station_id, line_id) where line_id not in (
            select line_id from topology_edges
        ) group by station_id
    ) r (station_id, line_id) where r.station_id = n.station_id;

insert into removed_nodes (station_id, location)
     select station_id, station_location
       from topology_nodes where array_length(line_id, 1) is null;
delete from topology_nodes where station_id in (select station_id from removed_nodes);

-- this cannot result into newly 'dangling edges', because if those
-- nodes were connected to anything, they wouldn't have been removed.

commit;

