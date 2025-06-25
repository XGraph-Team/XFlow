begin;
drop table if exists heuristic_links cascade;
drop table if exists heuristic_vertices cascade;
drop table if exists heuristic_vertices_highvoltage;
drop table if exists heuristic_links_highvoltage;

-- simplify to format of scigrid export
-- v_id,lon,lat,typ,voltage,frequency,name,operator,ref,wkt_srid_4326
create table heuristic_vertices (
    v_id        integer primary key,
    lon         float,
    lat         float,
    typ         text,
    voltage     text,
    frequency   text,
    name        text,
    operator    text,
    ref         text,
    wkt_srid_4326 text
);

-- l_id,v_id_1,v_id_2,voltage,cables,wires,frequency,name,operator,ref,length_m,r_ohmkm,x_ohmkm,c_nfkm,i_th_max_a,from_relation,wkt_srid_4326
create table heuristic_links (
    l_id        integer primary key,
    v_id_1      integer references heuristic_vertices (v_id),
    v_id_2      integer references heuristic_vertices (v_id),
    voltage     text,
    cables      text,
    wires       text,
    frequency   text,
    name        text,
    operator    text,
    ref         text,
    length_m    float,
    r_ohmkm     float,
    x_ohmkm     float,
    c_nfkm      float,
    i_th_max_a  float,
    from_relation text,
    wkt_srid_4326 text
);

insert into heuristic_vertices (v_id, lon, lat, typ, voltage, frequency, name, operator, ref, wkt_srid_4326)
    select n.station_id,
           ST_X(ST_Transform(station_location, 4326)),
           ST_Y(ST_Transform(station_location, 4326)),
           n.topology_name,
           array_to_string(e.voltage, ';'),
           array_to_string(e.frequency, ';'),
           e.name,
           e.operator,
           t.tags->'ref',
           ST_AsEWKT(ST_Transform(station_location, 4326))
           from topology_nodes n
           join electrical_properties e on e.power_id = n.station_id and e.power_type = 's'
           join osm_tags t              on t.power_id = n.station_id and t.power_type = 's';


insert into heuristic_links (l_id, v_id_1, v_id_2, length_m, voltage, cables, wires, frequency, name, operator, ref, from_relation, wkt_srid_4326)
    select l.line_id,
           l.station_id[1],
           l.station_id[2],
           st_length(st_transform(l.line_extent, 4326)::geography),
           array_to_string(e.voltage, ';'),
           array_to_string(e.conductor_bundles, ';'),
           array_to_string(e.subconductors, ';'),
           array_to_string(e.frequency, ';'),
           e.name,
           e.operator,
           t.tags->'ref', '',
           ST_AsEWKT(ST_Transform(direct_line, 4326))
           from topology_edges l
           join electrical_properties e on e.power_id = l.line_id and e.power_type = 'l'
           join osm_tags t              on t.power_id = l.line_id and t.power_type = 'l';

create table heuristic_vertices_highvoltage as
    select * from heuristic_vertices where v_id in (select station_id from high_voltage_nodes);

create table heuristic_links_highvoltage as
   select * from heuristic_links where l_id in (select line_id from high_voltage_edges);



commit;
