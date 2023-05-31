import networkx as nx
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.nn.inits import reset
import random
import numpy as np
from torch_geometric import utils
import scipy
import ndlib
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
import statistics as s
import time
from util import combinations, substract, subcombs

def scoreIC(g, config, node, seedset):
    backup = []
    for item in seedset:
        backup.append(item)
    backup.remove(node)

    total = []

    for i in range(1000):
        g_mid = g.__class__()
        g_mid.add_nodes_from(g)
        g_mid.add_edges_from(g.edges)

        model_mid = ep.IndependentCascadesModel(g_mid)
        config_mid = mc.Configuration()
        config_mid.add_model_initial_configuration('Infected', backup)

        for a, b in g_mid.edges():
            weight = config.config["edges"]['threshold'][(a, b)]
            g_mid[a][b]['weight'] = weight
            config_mid.add_edge_configuration('threshold', (a, b), weight)

        model_mid.set_initial_status(config_mid)

        iterations = model_mid.iteration_bunch(5)
        trends = model_mid.build_trends(iterations)

        total_no = 0

        for i in range(5):
            a = iterations[i]['node_count'][1]
            total_no += a

        total.append(total_no)

    final = s.mean(total)

    return final

def Y(df):
    EY = s.mean(df['result'])
    VY = s.pvariance(df['result'])
    return EY, VY

def SobolT(df, result):
    sobolt = {}

    for node in result:

        backup = []
        for item in result:
            backup.append(item)

        backup.remove(node)

        var = []

        for sub in combinations(backup):

            means = []

            for case in combinations([node]):

                total = []

                seeds = sub + case

                subdf = df

                for item in result:
                    if item in seeds:
                        a = (subdf[item] == 1)
                    else:
                        a = (subdf[item] == 0)

                    subdf = subdf[a]

                means.append(s.mean(subdf['result']))
            var.append(s.pvariance(means))

        sobolt[node] = s.mean(var)

    return sobolt


def sobols(df, result):
    allsobol = {}

    for blist in combinations(result):
        if blist == []:
            continue

        rest = substract(result, blist)

        exp = []

        for comb in combinations(blist):
            means = []

            for sub in combinations(rest):
                totals = []
                seeds = comb + sub

                conditions =[]

                #subdf = df
                for item in result:
                    if item in seeds:
                        a = (df[item] == 1)
                    else:
                        a = (df[item] == 0)
                    #subdf = df[a]
                    conditions.append(a)
                subdf = df[conditions[0] & conditions[1] & conditions[2] & conditions[3] & conditions[4]]

                means.append(s.mean(subdf['result']))

            exp.append(s.mean(means))

        if len(blist) == 1:
            score = s.pvariance(exp)
        else:
            sumsobol = 0
            for item in subcombs(blist):
                string = ''
                for thing in item:
                    string += str(thing)
                    string += '.'
                sumsobol += allsobol[string]
            score = s.pvariance(exp) - sumsobol

        string = ''
        for item in blist:
            string += str(item)
            string += '.'

        allsobol[string] = score

    sorted_sobol = {}
    for k in sorted(allsobol, key=len):
        sorted_sobol[k] = allsobol[k]
   
    return sorted_sobol

def IE(df, result):
    full = df[(df[result[0]] == 1) & (df[result[1]] == 1) & (df[result[2]] == 1) & (df[result[3]] == 1) & (df[result[4]] == 1)]
    E = s.mean(full['result'])
    std = s.stdev(full['result'])
    return E, std
'''
# sobol total of a set sized-k
def STS(df, result):
    k = int(0.5*len(result))

    sobolt = {}

    for set in combinations(result):

        if len(set) < k:
            continue
        if len(set) > k:
            break

        name = ''
        for item in set:
            name += str(item)
            name += '.'

        backup = []
        for item in result:
            backup.append(item)

        backup = substract(backup, set)

        var = []

        for sub in combinations(backup):

            means = []

            for case in combinations(set):

                total = []

                seeds = sub + case

                subdf = df

                for item in result:
                    if item in seeds:
                        a = (subdf[item] == 1)
                    else:
                        a = (subdf[item] == 0)

                    subdf = subdf[a]

                means.append(s.mean(subdf['result']))
            var.append(s.pvariance(means))

        sobolt[name] = s.mean(var)

    return sobolt
'''
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
