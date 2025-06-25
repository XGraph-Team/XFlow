drop table if exists invalid_polygons;
create table invalid_polygons as
select station_id, osm_id, polygon
  from (
       select o.power_id, o.osm_id,
              case when st_isclosed(wg.line) and st_numpoints(wg.line) > 3 then st_makepolygon(wg.line)
                   when st_numpoints(wg.line) >= 3
                   -- looks like an unclosed polygon based on endpoints distance
                     and st_distance(st_startpoint(wg.line), st_endpoint(wg.line)) < (st_length(wg.line) / 2)
                    then st_makepolygon(st_addpoint(wg.line, st_startpoint(wg.line)))
                    else null end
         from source_objects o
         join way_geometry wg on o.osm_id = wg.way_id
        where o.power_type = 's' and o.osm_type = 'w'
      ) _g(station_id, osm_id, polygon)
     -- even so not all polygons will be valid
  where polygon is not null and not st_isvalid(polygon);
