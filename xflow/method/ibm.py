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
from xflow.diffusion.SI import SI
from xflow.diffusion.IC import IC
from xflow.diffusion.LT import LT
# random

# baselines: simulation based

# greedy
def greedy(g, config, budget, seeds, rounds=100, model='SI', beta=0.1):

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

            if (model == "IC"):
                result = IC(g_greedy, config, seeds, rounds)
            if (model == "LT"):
                result = LT(g_greedy, config, seeds, rounds)
            if (model == "SI"):
                result = SI(g_greedy, config, seeds, rounds, beta)
            
            if s.mean(result) < min:
                min = s.mean(result)
                index = node

        selected.append(index)
        candidates.remove(index)

    print(selected)
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

    print(eig)
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

    print(deg)
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
    
    print(result)
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

    print(result)
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

    print(nodes)
    return nodes