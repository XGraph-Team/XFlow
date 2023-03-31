import networkx as nx
from time import time

from graphGeneration import Cora, CiteSeer, PubMed, connSW, ER, coms, photo
from IM import eigen, degree, pi, sigma, Netshield, Soboldeg, Soboleigen, SobolPi, SobolSigma, SobolNS, greedyIC, degreeDis,SoboldegreeDis
from score import effectIC
import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as ep
import matplotlib.pyplot as plt
import pandas as pd

g = nx.karate_club_graph()
config = mc.Configuration()
for a, b in g.edges():
  weight = 0.1
  g[a][b]['weight'] = weight
  config.add_edge_configuration("threshold", (a, b), weight)
seeds = degree(g,config,2)
print(seeds)

g_mid = g.__class__()
g_mid.add_nodes_from(g)
g_mid.add_edges_from(g.edges)

model_mid = ep.SIModel(g_mid)  # Model SI
config_mid = mc.Configuration()
config_mid.add_model_initial_configuration('Infected', seeds)
config_mid.add_model_parameter('beta', 0.1)  # Beta

for a, b in g_mid.edges():
    weight = config.config["edges"]['threshold'][(a, b)]
    g_mid[a][b]['weight'] = weight
    config_mid.add_edge_configuration('threshold', (a, b), weight)

model_mid.set_initial_status(config_mid)

iterations = model_mid.iteration_bunch(5)
trends = model_mid.build_trends(iterations)

result = []
for item in seeds:
    result.append(item)

for j in range(1, 5):

    snapshot = list(iterations[j]['status'].keys())
    for item in snapshot:
        result.append(item)

observation = []
for node in range(g.number_of_nodes()):
    if node in result:
        observation.append(1)
    else:
        observation.append(0)

print(observation)

overlaps = []
observations = []

for i in range(10000):

    g_mid = g.__class__()
    g_mid.add_nodes_from(g)
    g_mid.add_edges_from(g.edges)

    model_mid = ep.SIModel(g_mid)  # Model SI
    config_mid = mc.Configuration()
    config_mid.add_model_initial_configuration('Infected', seeds)
    config_mid.add_model_parameter('beta', 0.1)  # Beta

    for a, b in g_mid.edges():
        weight = config.config["edges"]['threshold'][(a, b)]
        g_mid[a][b]['weight'] = weight
        config_mid.add_edge_configuration('threshold', (a, b), weight)

    model_mid.set_initial_status(config_mid)

    iterations = model_mid.iteration_bunch(10)  # 10 time steps
    trends = model_mid.build_trends(iterations)

    result = []
    for item in seeds:
        result.append(item)

    for j in range(1, 10):

        snapshot = list(iterations[j]['status'].keys())

        for item in snapshot:
            result.append(item)

    obs = []
    for node in range(g.number_of_nodes()):
        if node in result:
            obs.append(1)
        else:
            obs.append(0)

    result.sort()

    overlap = 0
    for node in range(g.number_of_nodes()):
        if obs[node] == observation[node]:
            overlap += 1

    overlaps.append(overlap / g.number_of_nodes())

    observations.append(obs)

plt.hist(overlaps)
plt.show()