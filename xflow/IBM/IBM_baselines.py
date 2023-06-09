import networkx as nx
import numpy as np
import ndlib
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
import statistics as s
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import random

# random

# baselines: simulation based

# greedy
def greedySI(g, config, budget, seeds, beta=0.1):


    selected = []
    candidates = list(g.nodes())

    for i in range(budget):

        min = float('inf')
        index = -1
        for node in candidates:

            g_greedy = g.__class__()
            g_greedy.add_nodes_from(g)
            g_greedy.add_edges_from(g.edges)
            for a, b in g_greedy.edges():
                weight = config.config["edges"]['threshold'][(a, b)]
                g_greedy[a][b]['weight'] = weight

            removed = selected + [node]
            for node in removed:
                g_greedy.remove_node(node)

            result = SI(g_greedy, config, seeds, beta=beta)
            # result = LT(g, config, seed)

            if s.mean(result) < min:
                min = s.mean(result)
                index = node

        selected.append(index)
        candidates.remove(index)

    return selected

def greedyIC(g, config, budget, seeds):


    selected = []
    candidates = list(g.nodes())

    for i in range(budget):

        min = float('inf')
        index = -1
        for node in candidates:

            g_greedy = g.__class__()
            g_greedy.add_nodes_from(g)
            g_greedy.add_edges_from(g.edges)
            for a, b in g_greedy.edges():
                weight = config.config["edges"]['threshold'][(a, b)]
                g_greedy[a][b]['weight'] = weight

            removed = selected + [node]
            for node in removed:
                g_greedy.remove_node(node)

            result = IC(g_greedy, config, seeds)
            # result = LT(g, config, seed)

            if s.mean(result) < min:
                min = s.mean(result)
                index = node

        selected.append(index)
        candidates.remove(index)

    return selected

# baselines: proxy based
# eigen centrality
def eigen(g, config, budget):
    g_eig = g.__class__()
    g_eig.add_nodes_from(g)
    g_eig.add_edges_from(g.edges)
    for a, b in g_eig.edges():
        weight = config.config["edges"]['threshold'][(a, b)]
        g_eig[a][b]['weight'] = weight

    eig = []

    for k in range(budget):
        eigen = nx.eigenvector_centrality_numpy(g_eig)
        selected = sorted(eigen, key=eigen.get, reverse=True)[0]
        eig.append(selected)
        g_eig.remove_node(selected)

    return eig


# degree
def degree(g, config, budget):
    g_deg = g.__class__()
    g_deg.add_nodes_from(g)
    g_deg.add_edges_from(g.edges)
    for a, b in g_deg.edges():
        weight = config.config["edges"]['threshold'][(a, b)]
        g_deg[a][b]['weight'] = weight

    deg = []

    for k in range(budget):
        degree = nx.centrality.degree_centrality(g_deg)
        selected = sorted(degree, key=degree.get, reverse=True)[0]
        deg.append(selected)
        g_deg.remove_node(selected)

    return deg


# pi
def pi(g, config, budget):
    g_greedy = g.__class__()
    g_greedy.add_nodes_from(g)
    g_greedy.add_edges_from(g.edges)

    for a, b in g_greedy.edges():
        weight = config.config["edges"]['threshold'][(a, b)]
        g_greedy[a][b]['weight'] = weight

    result = []

    for k in range(budget):

        n = g_greedy.number_of_nodes()

        I = np.ones((n, 1))

        C = np.ones((n, n))
        N = np.ones((n, n))

        A = nx.convert_matrix.to_numpy_array(g_greedy, nodelist=list(g_greedy.nodes()))

        for i in range(5):
            B = np.power(A, i + 1)
            D = C - B
            N = np.multiply(N, D)

        P = C - N

        pi = np.matmul(P, I)

        value = {}

        for i in range(n):
            value[list(g_greedy.nodes())[i]] = pi[i, 0]

        selected = sorted(value, key=value.get, reverse=True)[0]

        result.append(selected)

        g_greedy.remove_node(selected)

    return result


# sigma
def sigma(g, config, budget):
    g_greedy = g.__class__()
    g_greedy.add_nodes_from(g)
    g_greedy.add_edges_from(g.edges)

    for a, b in g_greedy.edges():
        weight = config.config["edges"]['threshold'][(a, b)]
        g_greedy[a][b]['weight'] = weight

    result = []

    for k in range(budget):

        n = g_greedy.number_of_nodes()

        I = np.ones((n, 1))

        F = np.ones((n, n))
        N = np.ones((n, n))

        A = nx.convert_matrix.to_numpy_array(g, nodelist=g_greedy.nodes())

        sigma = I
        for i in range(5):
            B = np.power(A, i + 1)
            C = np.matmul(B, I)
            sigma += C

        value = {}

        for i in range(n):
            value[list(g_greedy.nodes())[i]] = sigma[i, 0]

        selected = sorted(value, key=value.get, reverse=True)[0]

        result.append(selected)

        g_greedy.remove_node(selected)

    return result

def Netshield(g, config, budget):

    g_greedy = g.__class__()
    g_greedy.add_nodes_from(g)
    g_greedy.add_edges_from(g.edges)

    for a, b in g_greedy.edges():
        weight = config.config["edges"]['threshold'][(a, b)]
        g_greedy[a][b]['weight'] = weight

    A = nx.adjacency_matrix(g_greedy)

    lam, u = np.linalg.eigh(A.toarray())
    lam = list(lam)
    lam = lam[-1]

    u = u[:, -1]

    u = np.abs(np.real(u).flatten())
    v = (2 * lam * np.ones(len(u))) * np.power(u, 2)

    nodes = []
    for i in range(budget):
        B = A[:, nodes]
        b = B * u[nodes]

        score = v - 2 * b * u
        score[nodes] = -1

        nodes.append(np.argmax(score))

    return nodes


# diffusion models
def IC(g, config, seed):
    # number of Monte Carlo simulations to be run for the IC model
    mc_number = 100
    result = []

    for iter in range(mc_number):

        model_temp = ep.IndependentCascadesModel(g)  # _temp
        config_temp = mc.Configuration()
        config_temp.add_model_initial_configuration('Infected', seed)

        for a, b in g.edges():  # _temp
            weight = config.config["edges"]['threshold'][(a, b)]
            # g_temp[a][b]['weight'] = weight
            config_temp.add_edge_configuration('threshold', (a, b), weight)

        model_temp.set_initial_status(config_temp)

        iterations = model_temp.iteration_bunch(5)

        total_no = 0

        for j in range(5):
            a = iterations[j]['node_count'][1]
            total_no += a

        result.append(total_no)

    return result


def LT(g, config, seed):
    # number of Monte Carlo simulations to be run for the LT model
    mc_number = 100
    result = []

    for iter in range(mc_number):

        model_temp = ep.ThresholdModel(g)  # _temp
        config_temp = mc.Configuration()
        config_temp.add_model_initial_configuration('Infected', seed)

        for a, b in g.edges():  # _temp
            weight = config.config["edges"]['threshold'][(a, b)]
            # g_temp[a][b]['weight'] = weight
            config_temp.add_edge_configuration('threshold', (a, b), weight)

        for i in g.nodes():
            threshold = random.randrange(1, 20)
            threshold = round(threshold / 100, 2)
            config_temp.add_node_configuration("threshold", i, threshold)

        model_temp.set_initial_status(config_temp)

        iterations = model_temp.iteration_bunch(5)

        total_no = iterations[4]['node_count'][1]

        result.append(total_no)

    return result


def SI(g, config, seeds, rounds=100, beta=0.1):

    result = []

    for iter in range(rounds):

        model_temp = ep.SIModel(g) # _temp
        config_temp = mc.Configuration()
        config_temp.add_model_initial_configuration('Infected', seeds)
        config_temp.add_model_parameter('beta', beta)

        for a, b in g.edges(): # _temp
            weight = config.config["edges"]['threshold'][(a, b)]
            config_temp.add_edge_configuration('threshold', (a, b), weight)

        model_temp.set_initial_status(config_temp)

        iterations = model_temp.iteration_bunch(5)

        result.append(iterations[4]['node_count'][1])

    return result