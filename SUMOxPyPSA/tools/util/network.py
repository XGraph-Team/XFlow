from __future__ import unicode_literals, division, print_function
import io
import csv
import random
import itertools
import heapq
import math
import warnings
try:
    from recordclass import recordclass
except ImportError:
    from collections import namedtuple as recordclass
    warnings.warn("recordclass is necessary for Network.patch() to work")

try:
    from numpy import array
    from matplotlib import pyplot
except ImportError as e:
    warnings.warn(str(e))




class Station(recordclass('Station', str('station_id lat lon name operator voltages frequencies lines'))):
    def __hash__(self):
        return hash(self.station_id)

    @property
    def coordinates(self):
        return self.lon, self.lat

    def distance(self, other):
        # See https://www.math.ksu.edu/~dbski/writings/haversine.pdf
        # earths radius will be 6.371 km
        R  = 6372.8
        delta_lat = math.radians(other.lat - self.lat)
        delta_lon = math.radians(other.lon - self.lon)
        a = math.sin(delta_lat/2)**2 + math.cos(math.radians(self.lat))*math.cos(math.radians(other.lat))*math.sin(delta_lon/2)**2
        c = 2*math.asin(math.sqrt(a))
        return R*c


    def to_ewkt(self):
        return 'SRID=4326;POINT({0} {1})'.format(self.lon, self.lat)


class Line(recordclass('Line', str('line_id operator left right length frequencies voltages resistance reactance capacitance max_current'))):
    def __hash__(self):
        return hash(self.line_id)

    def __repr__(self):
        return "{0}: {1} -> {2}".format(self.line_id, self.left.name, self.right.name).encode('utf-8')

    @property
    def susceptance(self):
        if self.capacitance is None or not self.frequencies:
            return None
        return self.capacitance * max(self.frequencies)

class Path(object):
    def __init__(self, stations):
        self.stations = stations
        # make list of lines
        self.lines    = list()
        for i in range(1, len(stations)):
            f = stations[i-1]
            t = stations[i]
            for l in f.lines:
                if f is l.left:
                    if t is l.right:
                        break
                elif t is l.left:
                    break
            self.lines.append(l)

    def plot(self, figure=None, color='yellow'):
        if figure is None:
            figure = pyplot.figure()
        axs = figure.add_subplot(1,1,1)
        lat = [s.lat for s in self.stations]
        lon = [s.lon for s in self.stations]
        axs.plot(lon,lat, color=color)
        return figure

    @property
    def length(self):
        return sum(l.length for l in self.lines)

    def __iter__(self):
        return iter(self.stations)

    def __repr__(self):
        return 'Path of length {0} over [{1}]'.format(
            self.length, ', '.join(s.name for s in self.stations)
        ).encode('utf-8')

    def to_ewkt(self):
        return 'SRID=4326;LINESTRING({0})'.format(
            ','.join('{0} {1}'.format(s.lon, s.lat) for s in self.stations)
        )



class Network(object):
    def __init__(self):
        self.stations = dict()
        self.lines    = dict()
        self._areas   = dict()

    def connected_sets(self):
        # bfs algorithm to find connected sets in the network
        unseen = set(self.stations.values())
        connected = []
        while unseen:
            current = []
            root  = unseen.pop()
            queue = [root]
            while queue:
                node = queue.pop()
                if node in unseen:
                    unseen.remove(node)
                    current.append(node)
                for line in node.lines:
                    if line.left in unseen:
                        queue.append(line.left)
                    if line.right in unseen:
                        queue.append(line.right)
            connected.append(current)
        return connected

    def patch(self):
        # flood algorithm to patch all lines and stations with values from neighbours
        totals = list()
        while True:
            changes = 0
            for station in self.stations.itervalues():
                line_voltages    = set(v for line in station.lines for v in line.voltages)
                line_frequencies = set(f for line in station.lines for f in line.frequencies)
                if line_voltages - station.voltages:
                    station.voltages |= line_voltages
                    changes          += 1
                if line_frequencies - station.frequencies:
                    station.frequencies |= line_frequencies
                    changes             += 1


            for line in self.lines.itervalues():
                shared_frequencies = line.left.frequencies & line.right.frequencies
                if shared_frequencies and not line.frequencies & shared_frequencies:
                    line.frequencies |= shared_frequencies
                    changes += 1
                elif not line.frequencies:
                    if line.left.frequencies:
                        line.frequencies = set(line.left.frequencies)
                        changes += 1
                    elif line.right.frequencies:
                        line.frequencies = set(line.right.frequencies)
                        changes += 1

                shared_voltages = line.left.voltages & line.right.voltages
                if shared_voltages and not line.voltages & shared_voltages:
                    line.voltages |= shared_voltages
                    changes += 1
                elif not line.voltages:
                    if line.left.voltages:
                        line.voltages = set(line.left.voltages)
                        changes += 1
                    elif line.right.voltages:
                        line.voltages = set(line.right.voltages)
                        changes += 1

            if changes == 0:
                break
            totals.append(changes)
            if len(totals) > 1000:
                raise Exception('dont think ill be stopping soon')
        return totals

    def report(self):
        # calculate missing values statically
        broken_stations = 0
        broken_lines    = 0
        mismatches      = 0
        for station in self.stations.itervalues():
            if not station.voltages or not station.frequencies:
                broken_stations += 1
            for line in station.lines:
                if station.frequencies:
                    if line.frequencies - station.frequencies:
                        mismatches += 1
                        continue
                elif line.frequencies:
                    mismatches += 1
                    continue
                if station.voltages:
                    if line.voltages - station.voltages:
                        mismatches += 1
                        continue
                elif line.voltages:
                    mismatches += 1
                    continue

        for line in self.lines.itervalues():
            if not line.voltages or not line.frequencies:
                broken_lines += 1
        return broken_stations, broken_lines, mismatches

    def find(self, from_id, to_id):
        # A* algorithm to find shortest path
        scores    = dict()
        come_from = dict()
        seen      = set()
        path      = list()
        try:
            start     = self.stations[from_id]
            goal      = self.stations[to_id]
        except KeyError:
            return None
        queue     = [(0,start)]
        while queue:
            score, station = heapq.heappop(queue)
            if station is goal:
                break
            seen.add(station)
            for line in station.lines:
                neighbor = line.left if line.right is station else line.right
                if neighbor in seen:
                    continue
                g_score = score + line.length
                if scores.get(neighbor, g_score+1) < g_score:
                    continue
                h_score = goal.distance(neighbor)
                heapq.heappush(queue, (g_score + h_score, neighbor))
                come_from[neighbor] = station
        if station is not goal:
            return None
        while station is not start:
            path.append(station)
            station = come_from[station]
        path.append(start)
        path.reverse()
        return Path(path)


    def plot(self, figure=None, node_color='blue', edge_color='red'):
        if figure is None:
            figure = pyplot.figure()
        axis = figure.add_subplot(1,1,1)
        for line in self.lines.values():
            axis.plot([line.left.lon, line.right.lon],
                      [line.left.lat, line.right.lat], color=edge_color)
        coordinates = [s.coordinates for s in self.stations.values()]
        axis.plot(*zip(*coordinates), marker='o', color=node_color, lineStyle='None')
        return figure

    def _area_number(self, area_name):
        if area_name not in self._areas:
            # assign next area number
            self._areas[area_name] = len(self._areas) + 1
        return self._areas[area_name]

    def powercase(self, loads=None):
        # loads is a map of station id -> load, either positive or
        # negative; a negative load is represented by a generator.

        # if no loads map is passed, generate an 'electrified pair' of
        # two random nodes, one of which delivers power, the other
        # consumes it
        if loads is None:
            loads = self._electrified_pair()
        ppc = {
            "version": 2,
            "baseMVA": 100.0
        }
        nodes        = list()
        edges        = list()
        generators   = list()

        station_to_bus = dict()
        bus_id_gen     = itertools.count()

        for station in self.stations.itervalues():
            # because we do a DC PF, we ignore frequencies completely
            minv, maxv = min(station.voltages), max(station.voltages)
            for voltage in station.voltages:
                if station.station_id in loads and voltage == minv:
                    bus_load = loads[station.station_id]
                else:
                    bus_load = 0
                bus_id = next(bus_id_gen)
                station_to_bus[station.station_id, voltage] = bus_id
                if bus_load < 0:
                    # it is a generator instead of a load, insert it
                    generators.append(self._make_generator(bus_id, -bus_load))
                    bus_load = 0
                nodes.append(self._make_bus(station, voltage, bus_load, bus_id))

            for voltage in station.voltages:
                if voltage != maxv:
                    # create a transformer branch from max voltage to this voltage
                    from_bus = station_to_bus[station.station_id, maxv]
                    to_bus   = station_to_bus[station.station_id, voltage]
                    edges.append(self._make_transformer(from_bus, to_bus))

        for line in self.lines.itervalues():
            # create branches between stations
            for voltage in line.voltages:
                from_bus = station_to_bus[line.left.station_id, voltage]
                to_bus   = station_to_bus[line.right.station_id, voltage]
                edges.append(self._make_line(line, from_bus, to_bus))

        ppc['bus']    = array(nodes)
        ppc['gen']    = array(generators)
        ppc['branch'] = array(edges)
        return ppc

    def _electrified_pair(self):
        src, dst = random.sample(self.stations, 2)
        return {
            src: -100, # MW
            dst: 50,  # MW
        }

    def _make_bus(self, station, voltage, load, bus_id):
        # see pypower.caseformat for documentation on how this works
        area_nr  = self._area_number(station.operator)
        base_kv  = voltage // 1000
        return [
            bus_id,
            3,       # slack bus
            load,    # real load in MW
            0,       # reactive load MVAr, zero because DC
            0,       # shunt conductance
            0,       # shunt susceptance
            area_nr, # area number
            1.0,     # voltage magnitude per unit
            0,       # voltage angle
            base_kv, # base voltage (per unit base)
            area_nr, # loss zone nr
            1.1,     # max voltage per unit
            0.9,     # min voltage per unit
        ]

    def _make_transformer(self, from_bus, to_bus):
        return [
            from_bus,
            to_bus,
            0.01,      # resistance
            0.01,      # reactance
            0.01,      # line charging susceptance
            200,       # long term rating (MW)
            200,       # short term rating (MW)
            200,       # emergency rating (MW)
            1,         # off-nominal (correction) taps ratio, 1 for no correction
            0,         # transformer phase shift angle,
            1,         # status (1 = on)
            -360,      # minimum angle
            360,       # maximum angle
        ]

    def _make_line(self, line, from_bus, to_bus):
        return [
            from_bus,
            to_bus,
            line.resistance or 0.01,   # default value if None
            line.reactance or 0.01,
            line.susceptance or 0.01,
            200,
            200,
            200,
            0,                          # not a transformer
            0,                          # not a transformer
            1,                          # status
            -360,
            360
        ]

    def _make_generator(self, bus_id, power_output):
        return [
            bus_id,
            power_output,
            0,             # reactive power output
            0,             # maximum reactive power output
            0,             # minimum reactive power output
            1.0,           # per-unit voltage magnitude setpoint
            100,           # base MVA
            1,             # status (on)
            power_output,  # maximum real power output
            0,             # minimum real power output
            0,             # Pc1, irrelevant
            0,             # Pc2
            0,             # Qc1min
            0,             # Qc1max
            0,             # Qc2min
            0,             # Qc2max
            5,             # ramp rate load-following (MW/min)
            5,             # ramp rate 10-min reserve (MW/min)
            5,             # ramp rate 30-min reserve (MW/min)
            0,             # ramp rate reactive power
            0,             # area participation factor
        ]
        pass


    def dot(self):
        buf = io.StringIO()
        buf.write("graph {\n")
        buf.write("rankdir LR\n")
        for station in self.stations.itervalues():
            buf.write('s_{0} [label="{1}"]\n'.format(station.station_id, station.name.replace('"', "'")))
        for line in self.lines.itervalues():
            buf.write('s_{0} -- s_{1}\n'.format(line.left.station_id, line.right.station_id))
        buf.write("}\n")
        return buf.getvalue()

    def __repr__(self):
        return "Network of {0} stations, {1} lines".format(len(self.stations), len(self.lines)).encode('utf-8')


class ScigridNetwork(Network):
    class _csv_dialect(csv.excel):
        quotechar = b"'"

    def read(self, vertices_csv, links_csv):
        with io.open(vertices_csv, 'rb') as handle:
            for row in csv.DictReader(handle, dialect=self._csv_dialect):
                station_id  = int(row['v_id'])
                lat         = float(row['lat'])
                lon         = float(row['lon'])
                name        = row['name'].decode('utf-8')
                operator    = row['operator'].decode('utf-8')
                voltages    = set(map(int, row['voltage'].split(';')) if row['voltage'] else [])
                frequencies = set(map(float, row['frequency'].split(';')) if row['frequency'] else [])
                self.stations[station_id] = Station(station_id=station_id, lat=lat, lon=lon, name=name, operator=operator,
                                                    voltages=voltages, frequencies=frequencies, lines=list())

        with io.open(links_csv, 'rb') as handle:
            for i, row in enumerate(csv.DictReader(handle, dialect=self._csv_dialect)):
                line_id     = int(row['l_id'])
                operator    = row['operator'].decode('utf-8')
                left        = self.stations[int(row['v_id_1'])]
                right       = self.stations[int(row['v_id_2'])]
                length      = float(row['length_m'])
                resistance  = float(row['r_ohmkm']) * int(row['length_m']) / 1000 if row['r_ohmkm'] else None
                reactance   = float(row['x_ohmkm']) * int(row['length_m']) / 1000 if row['x_ohmkm'] else None
                capacitance = float(row['c_nfkm']) * int(row['length_m']) / 1000  if row['c_nfkm'] else  None
                max_current = float(row['i_th_max_a']) if row['i_th_max_a'] else None
                # use complex voltages for lines
                frequencies = set(map(float, row['frequency'].split(';')) if row['frequency'] else [])
                voltages    = set(map(int, row['voltage'].split(';')) if row['voltage'] else [])
                line  = Line(line_id=line_id, operator=operator, left=left, right=right, length=length,
                             voltages=voltages, frequencies=frequencies,
                             resistance=resistance, reactance=reactance, capacitance=capacitance,
                             max_current=max_current)
                self.lines[line_id] = line
                left.lines.append(line)
                right.lines.append(line)

