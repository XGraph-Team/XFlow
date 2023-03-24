import networkx as nx
import numpy as np
from simulation import simulationIC, simulationLT
#from score import SobolT
import ndlib
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
import statistics as s
import heapdict as hd
import random
import heapq

# baseline 1 Eigen centrality 
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

# baseline 2 degree
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

# baseline 3 pi (proxy)
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

        A = nx.to_numpy_matrix(g_greedy, nodelist=list(g_greedy.nodes()))

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

# baseline 4 sigma (proxy)
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

        A = nx.to_numpy_matrix(g, nodelist=g_greedy.nodes())

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

# baseline 5.1 simulation based greedy
def greedyIC(g, config, budget):

    selected = []
    candidates = []

    for node in g.nodes():
        candidates.append(node)

    for i in range(budget):
        max = 0
        index = -1
        for node in candidates:
            seed = []
            for item in selected:
                seed.append(item)
            seed.append(node)

            # g_temp = g.__class__()
            # g_temp.add_nodes_from(g)
            # g_temp.add_edges_from(g.edges)
            result = []

            for iter in range(100):

                model_temp = ep.IndependentCascadesModel(g) # _temp
                config_temp = mc.Configuration()
                config_temp.add_model_initial_configuration('Infected', seed)

                for a, b in g.edges(): # _temp
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

            if s.mean(result) > max:
                max = s.mean(result)
                index = node

        selected.append(index)
        candidates.remove(index)

    return selected

# baseline 5.2 simulation based greedy
def greedyLT(g, config, budget):

    selected = []
    candidates = []

    for node in g.nodes():
        candidates.append(node)

    for i in range(budget):
        max = 0
        index = -1
        for node in candidates:
            seed = []
            for item in selected:
                seed.append(item)
            seed.append(node)

            # g_temp = g.__class__()
            # g_temp.add_nodes_from(g)
            # g_temp.add_edges_from(g.edges)
            result = []

            for iter in range(100):

                model_temp = ep.ThresholdModel(g) # _temp
                config_temp = mc.Configuration()
                config_temp.add_model_initial_configuration('Infected', seed)

                for a, b in g.edges(): # _temp
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

            if s.mean(result) > max:
                max = s.mean(result)
                index = node

        selected.append(index)
        candidates.remove(index)

    return selected

# baseline 6 random

# baseline 7 simulation

# baseline 8 sketch base

# baseline 9.1 CELF
def celf(g, config, budget):

    selected = []
    candidates = list(g.nodes())

    gains = []
    for node in candidates:
        seed = selected + [node]
        result = IC(g, config, seed)
        gain = s.mean(result)
        # heapq min-heap
        heapq.heappush(gains, (-gain, node))

    for i in range(budget):
        while True:
            gain, node = heapq.heappop(gains)
            seed = selected + [node]
            result = IC(g, config, seed)
            new_gain = s.mean(result)
            if new_gain == -gain:
                break
            else:
                heapq.heappush(gains, (-new_gain, node))

        selected.append(node)
        candidates.remove(node)

    return selected

# baseline 9.2 CELFPP
def celfpp(g, config, budget):
    selected = []
    candidates = list(g.nodes())

    gains = []
    for node in candidates:
        seed = selected + [node]
        result = IC(g, config, seed)
        gain = s.mean(result)
        heapq.heappush(gains, (-gain, node, None))

    last_seed = None

    for i in range(budget):
        while True:
            gain, node, last_added_seed = heapq.heappop(gains)

            if last_added_seed == last_seed:
                new_gain = -gain
            else:
                seed = selected + [node]
                result = IC(g, config, seed)
                new_gain = s.mean(result)

            if new_gain == -gain:
                break
            else:
                heapq.heappush(gains, (-new_gain, node, last_seed))

        selected.append(node)
        candidates.remove(node)
        last_seed = node

    return selected

# greedy -> CELF/CELFPP -> IC/LT
def greedy(g, config, budget):

    selected = []
    candidates = list(g.nodes())

    for i in range(budget):
        max = 0
        index = -1
        for node in candidates:
            seed = selected + [node]

            result = IC(g, config, seed)
            #result = LT(g, config, seed)

            if s.mean(result) > max:
                max = s.mean(result)
                index = node

        selected.append(index)
        candidates.remove(index)

    return selected

def IC(g, config, seed):
    # number of Monte Carlo simulations to be run for the IC model
    mc_number = 100
    result = []

    for iter in range(mc_number):

        model_temp = ep.IndependentCascadesModel(g) # _temp
        config_temp = mc.Configuration()
        config_temp.add_model_initial_configuration('Infected', seed)

        for a, b in g.edges(): # _temp
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

        model_temp = ep.ThresholdModel(g) # _temp
        config_temp = mc.Configuration()
        config_temp.add_model_initial_configuration('Infected', seed)

        for a, b in g.edges(): # _temp
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
