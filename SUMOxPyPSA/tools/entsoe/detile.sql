begin;
drop table if exists tile_split_lines;
create table tile_split_lines (
    short_id integer,
    long_id integer,
    short_line geometry(linestring,4326),
    long_line geometry(linestring,4326)
);

insert into tile_split_lines (short_id, long_id, short_line, long_line)
     select a.import_id, b.import_id, a.line, b.line
       from feature_lines a, feature_lines b
      where a.properties->'objectid' != '0'
        and a.properties->'objectid' = b.properties->'objectid'
        and st_length(a.line) < st_length(b.line);
commit;
