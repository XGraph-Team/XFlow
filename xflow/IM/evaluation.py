import networkx as nx
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.nn.inits import reset
import random
import numpy as np
from torch_geometric import utils
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
import statistics as s

def effectIC(g, config, result):

    input = []

    for i in range(1000):

      g_mid = g.__class__()
      g_mid.add_nodes_from(g)
      g_mid.add_edges_from(g.edges)

      model_mid = ep.IndependentCascadesModel(g_mid)
      config_mid = mc.Configuration()
      config_mid.add_model_initial_configuration('Infected', result)

      for a, b in g_mid.edges():
        weight = config.config["edges"]['threshold'][(a, b)]
        g_mid[a][b]['weight'] = weight
        config_mid.add_edge_configuration('threshold', (a, b), weight)

      model_mid.set_initial_status(config_mid)

      iterations = model_mid.iteration_bunch(5)
      trends = model_mid.build_trends(iterations)

      total_no = 0

      for j in range(5):
        a = iterations[j]['node_count'][1]
        total_no += a

      input.append(total_no)

    e = s.mean(input)
    v = s.stdev(input)

    return e,v

def effectLT(g, config, result):

    input = []

    for i in range(1000):

      g_mid = g.__class__()
      g_mid.add_nodes_from(g)
      g_mid.add_edges_from(g.edges)

      model_mid = ep.ThresholdModel(g_mid)
      config_mid = mc.Configuration()
      config_mid.add_model_initial_configuration('Infected', result)

      for a, b in g_mid.edges():
        weight = config.config["edges"]['threshold'][(a, b)]
        g_mid[a][b]['weight'] = weight
        config_mid.add_edge_configuration('threshold', (a, b), weight)

      for i in g.nodes():
          threshold = random.randrange(1, 20)
          threshold = round(threshold / 100, 2)
          config_mid.add_node_configuration("threshold", i, threshold)

      model_mid.set_initial_status(config_mid)

      iterations = model_mid.iteration_bunch(5)
      trends = model_mid.build_trends(iterations)

      total_no = iterations[4]['node_count'][1]
      input.append(total_no)

    e = s.mean(input)
    v = s.stdev((input))

    return e,v

def effectSI(g, config, result, beta=0.01):

    input = []

    for i in range(1000):

        g_mid = g.__class__()
        g_mid.add_nodes_from(g)
        g_mid.add_edges_from(g.edges)

        model_mid = ep.SIModel(g_mid)
        config_mid = mc.Configuration()
        config_mid.add_model_initial_configuration('Infected', result)
        config_mid.add_model_parameter('beta', beta)  # set beta parameter


        for a, b in g_mid.edges():
            weight = config.config["edges"]['threshold'][(a, b)]
            g_mid[a][b]['weight'] = weight
            config_mid.add_edge_configuration('threshold', (a, b), weight)

        model_mid.set_initial_status(config_mid)

        iterations = model_mid.iteration_bunch(5)
        trends = model_mid.build_trends(iterations)

        total_no = iterations[4]['node_count'][1]
        input.append(total_no)

    e = s.mean(input)
    v = s.stdev((input))

    return e,v
