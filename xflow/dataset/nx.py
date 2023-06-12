import networkx as nx
import random
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc


def connSW(n, beta=None):
    g = nx.connected_watts_strogatz_graph(n, 10, 0.1)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        if beta:
            weight = beta
        g[a][b]['weight'] = weight
        config.add_edge_configuration("threshold", (a, b), weight)

    return g, config

def BA():
    g = nx.barabasi_albert_graph(1000, 5)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        g[a][b]['weight'] = weight
        config.add_edge_configuration("threshold", (a, b), weight)

    return g, config

def ER():
    g = nx.erdos_renyi_graph(5000, 0.002)

    while nx.is_connected(g) == False:
        g = nx.erdos_renyi_graph(5000, 0.002)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config
