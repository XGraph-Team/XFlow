begin;
drop table if exists line_neighbor_voltage_pairs;
drop table if exists base_probability;
drop table if exists conditional_probability;

create table line_voltage_distribution (
    voltage integer not null,
    line_count integer not null,
    primary key (voltage)
);

create table line_neighbor_voltage_pairs (
    line_voltage integer not null,
    neighbor_voltage integer not null,
    pair_count integer not null,
    primary key (line_voltage, neighbor_voltage)
);

create table base_probability (
    quantity    varchar(64) not null,
    prediction  integer not null,
    probability float not null,
    primary key (quantity, prediction)
);

create table conditional_probability (
     quantity    varchar(64) not null,
     conditional integer not null,
     prediction  integer not null,
     probability float not null,
     primary key (quantity, conditional, prediction)
);

-- compute all probabilities for line-neighbor voltage pairs
with voltage_pair (low_v, high_v, cnt) as (
    select least(a.voltage, b.voltage), greatest(a.voltage, b.voltage), count(*)
      from topology_nodes n
      join line_structure a on a.line_id = any(n.line_id)
      join line_structure b on b.line_id = any(n.line_id)
     where a.line_id < b.line_id
       and a.voltage is not null and b.voltage is not null
     group by least(a.voltage, b.voltage), greatest(a.voltage, b.voltage)
    having count(*) >= 10
)
insert into line_neighbor_voltage_pairs (line_voltage, neighbor_voltage, pair_count)
     select low_v, high_v, cnt from voltage_pair
      union
     select high_v, low_v, cnt from voltage_pair;

/* compute probabilities, recompute some values, but who cares */

insert into base_probability (quantity, prediction, probability)
     select 'line_voltage', line_voltage, (line_count * 1.0) / total_count
       from (
            select line_voltage, sum(pair_count)
              from line_neighbor_voltage_pairs
             group by line_voltage
          ) line_total (line_voltage, line_count),
           (
            select sum(pair_count) from line_neighbor_voltage_pairs
          ) pair_total (total_count);

insert into base_probability (quantity, prediction, probability)
     select 'neighbor_voltage', neighbor_voltage, (neighbor_count * 1.0) / total_count
       from (
            select neighbor_voltage, sum(pair_count)
              from line_neighbor_voltage_pairs
             group by neighbor_voltage
          ) neighbor_total (neighbor_voltage, neighbor_count),
           (
            select sum(pair_count) from line_neighbor_voltage_pairs
          ) pair_total (total_count);

insert into conditional_probability (quantity, conditional, prediction, probability)
     select 'neighbor_voltage_given_line_voltage', line_voltage, neighbor_voltage,
            (pair_count * 1.0)/line_total
      from line_neighbor_voltage_pairs
      join (
           select line_voltage, sum(pair_count)
             from line_neighbor_voltage_pairs
            group by line_voltage
         ) line_total (group_voltage, line_total)
        on group_voltage = line_voltage;


/* 
something is going very wrong, here!
select line_id, neighbor_voltage, f.prediction, "p(n|l)/p(n)"*probability from (
select l.line_id, ncp.conditional as prediction, array_agg(nl.line_id) as neighbor_id, array_agg(nl.voltage) as neighbor_voltage,
       exp(sum(log(nbp.probability)) - sum(log(ncp.probability))) as "p(n|l)/p(n)"
  from line_structure l
  join topology_nodes tn on l.line_id = any(tn.line_id)
  join line_structure nl on nl.line_id = any(tn.line_id)
  join conditional_probability ncp on ncp.quantity = 'neighbor_voltage_given_line_voltage' and ncp.prediction = nl.voltage
  join base_probability nbp on nbp.quantity = 'neighbor_voltage' and nbp.prediction = nl.voltage

 where l.voltage is null and nl.voltage is not null and l.line_id in (524, 1017)
group by l.line_id, ncp.conditional
) f join base_probability b on f.prediction = b.prediction and quantity = 'line_voltage'
order by line_id, "p(n|l)/p(n)"*probability desc;

*/
commit;
