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
from random import uniform, seed

from collections import Counter
import operator
import copy
from random import uniform, seed

# random

# baselines: simulation based

# greedy

def greedy(g, config, budget, rounds=100, model='SI', beta=0.1):
    model = model.upper()

    selected = []
    candidates = list(g.nodes())

    for i in range(budget):
        max_spread = 0
        index = -1
        for node in candidates:
            seed = selected + [node]

            if model == "IC":
                result = IC(g, config, seed, rounds)
            elif model == "LT":
                result = LT(g, config, seed, rounds)
            elif model == "SI":
                result = SI(g, config, seed, rounds, beta=beta)
            else:
                raise ValueError(f"Unknown model: {model}")

            mean_result = s.mean(result)
            if mean_result > max_spread:
                max_spread = mean_result
                index = node

        if index == -1:
            raise ValueError("No valid node found to select. Check the model implementation and input graph.")

        selected.append(index)
        candidates.remove(index)

    print(selected)
    return selected


def celf(g, config, budget, rounds=100, model='SI', beta=0.1): 
    model = model.upper()

    # Find the first node with greedy algorithm
    
    # Compute marginal gain for each node
    candidates = list(g.nodes())
    #, start_time = list(g.nodes()), time.time()
    # step 1, call a diffusion function, get the result of list
    # step 2, calculate the margin gain 
    if (model == "IC"):
        marg_gain = [s.mean(IC(g, config, [node])) for node in candidates]
    elif (model == "LT"):
        marg_gain = [s.mean(LT(g, config, [node])) for node in candidates]
    elif (model == "SI"):
         marg_gain = [s.mean(SI(g, config, [node], beta)) for node in candidates]
    # Create the sorted list of nodes and their marginal gain 
    Q = sorted(zip(candidates,marg_gain), key = lambda x: x[1],reverse=True)

    # Select the first node and remove from candidate list
    selected, spread, Q = [Q[0][0]], Q[0][1], Q[1:]
    
    # Find the next budget-1 nodes using the CELF list-sorting procedure
    
    for _ in range(budget-1):    

        check = False      
        while not check:
            
            # Recalculate spread of top node
            current = Q[0][0]
            
            # Evaluate the spread function and store the marginal gain in the list
            if (model == "IC"):
                Q[0] = (current, s.mean(IC(g, config, selected+[current]), rounds) - spread)
            elif (model == "LT"):
                Q[0] = (current, s.mean(LT(g, config, selected+[current]), rounds) - spread)
            elif (model == "SI"):
                Q[0] = (current, s.mean(SI(g, config, selected+[current]), rounds, beta) - spread)

            # Re-sort the list
            Q = sorted(Q, key = lambda x: x[1], reverse=True)

            # Check if previous top node stayed on top after the sort
            check = Q[0][0] == current

        # Select the next node
        selected.append(Q[0][0])
        spread = Q[0][1]
        
        # Remove the selected node from the list
        Q = Q[1:]

    print(selected)
    return(selected)
    # return(sorted(S),timelapse)

def celfpp(g, config, budget, rounds=100, model='SI', beta=0.1):
    model = model.upper()

    # Compute marginal gain for each node
    candidates = list(g.nodes())
    if (model == "IC"):
        marg_gain = [s.mean(IC(g, config, [node], rounds)) for node in candidates]
    elif (model == "LT"):
        marg_gain = [s.mean(LT(g, config, [node], rounds)) for node in candidates]
    elif (model == "SI"):
        marg_gain = [s.mean(SI(g, config, [node], rounds, beta)) for node in candidates]

    # Create the sorted list of nodes and their marginal gain 
    Q = sorted(zip(candidates, marg_gain), key = lambda x: x[1], reverse=True)

    # Select the first node and remove from candidate list
    selected, spread, Q = [Q[0][0]], Q[0][1], Q[1:]

    # Initialize last_seed as the first selected node
    last_seed = selected[0]
    
    # Find the next budget-1 nodes using the CELF++ procedure
    for _ in range(budget - 1):    
        check = False
        while not check:
            # Get current node and its previous computed marginal gain
            current, old_gain = Q[0][0], Q[0][1]

            # Check if the last added seed has changed
            if current != last_seed:
                # Compute new marginal gain
                if (model == "IC"):
                    new_gain = s.mean(IC(g, config, selected+[current], rounds)) - spread
                elif (model == "LT"):
                    new_gain = s.mean(LT(g, config, selected+[current], rounds)) - spread
                elif (model == "SI"):
                    new_gain = s.mean(SI(g, config, selected+[current], rounds, beta)) - spread
            else:
                # If the last added seed hasn't changed, the marginal gain remains the same
                new_gain = old_gain

            # Update the marginal gain of the current node
            Q[0] = (current, new_gain)

            # Re-sort the list
            Q = sorted(Q, key = lambda x: x[1], reverse=True)

            # Check if previous top node stayed on top after the sort
            check = Q[0][0] == current

        # Select the next node
        selected.append(Q[0][0])
        spread += Q[0][1]  # Update the spread
        last_seed = Q[0][0]  # Update the last added seed

        # Remove the selected node from the list
        Q = Q[1:]

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
        if nodes:
            B = A[:, nodes].toarray()
            b = np.dot(B, u[nodes])
        else:
            b = np.zeros_like(u)

        score = v - 2 * b * u
        score[nodes] = -1

        nodes.append(np.argmax(score))

    return nodes

####################################

# IMRank
# https://github.com/Braylon1002/IMTool
def IMRank(g, config, budget):
    """
    IMRank algorithm to rank the nodes based on their influence.
    """

    # Obtain adjacency matrix from the graph
    adjacency_matrix = nx.adjacency_matrix(g).todense()

    # Normalize the adjacency matrix
    row_sums = adjacency_matrix.sum(axis=1)
    
    # Check for zero entries in row_sums (which could correspond to isolated nodes)
    # and replace them with 1 to prevent division by zero errors
    row_sums[row_sums == 0] = 1

    adjacency_matrix = adjacency_matrix / row_sums
    
    start = time.perf_counter()
    t = 0
    r0 = [i for i in range(len(adjacency_matrix))]
    r = [0 for i in range(len(adjacency_matrix))]

    # Loop until the ranks converge
    while True:
        t = t + 1
        r = LFA(adjacency_matrix)
        r = np.argsort(-np.array(r))
        if operator.eq(list(r0), list(r)):
            break
        r0 = copy.copy(r)
        
    # Select top nodes up to the budget
    selected = r[:budget].tolist()

    print(selected)
    return selected

# baselines: sketch based

#RIS
# https://github.com/Braylon1002/IMTool
def RIS(g, config, budget, rounds=100):
#     mc = 100
    # Generate mc RRSs
    R = [get_RRS(g, config) for _ in range(rounds)]

    selected = []
    for _ in range(budget):
        # Collect all nodes from all RRSs
        flat_map = [item for subset in R for item in subset]
        # Only proceed if there are nodes in the flat_map
        if flat_map:
            seed = Counter(flat_map).most_common()[0][0]
            selected.append(seed)

            R = [rrs for rrs in R if seed not in rrs]

            # For every removed RRS, generate a new one
            while len(R) < rounds:
                R.append(get_RRS(g, config))

    print(selected)
    return (selected)

def LFA(matrix):
    """
    Linear Feedback Algorithm to update the ranks of the nodes.
    """
    n = len(matrix)
    Mr = [1 for _ in range(n)]
    Mr_next = Mr.copy()
    for i_ in range(1, n):
        i = n - i_
        for j in range(0, i + 1):
            Mr_next[j] = Mr_next[j] + matrix[j][i] * Mr[i]
            Mr_next[i] = (1 - matrix[j][i]) * Mr_next[i]
        Mr = Mr_next.copy()
    return Mr

############### IMM ################

import torch
import random
import time
import sys
import math

def sampling(epsoid, l, graph, node_num, seed_size, model):
    R = []
    LB = 1
    n = node_num
    k = seed_size
    epsoid_p = epsoid * math.sqrt(2)

    for i in range(1, int(math.log2(n-1))+1):
        s = time.time()
        x = n/(math.pow(2, i))
        lambda_p = ((2+2*epsoid_p/3)*(logcnk(n, k) + l*math.log(n) + math.log(math.log2(n)))*n)/pow(epsoid_p, 2)
        theta = lambda_p/x

        for _ in range(int(theta) - len(R)):
            v = random.randint(0, node_num - 1)
            rr = generate_rr(v, graph, node_num, model)
            R.append(rr)

        end = time.time()
        print('time to find rr', end - s)
        start = time.time()
        Si, f = node_selection(R, k, node_num)
        print(f)
        end = time.time()
        print('node selection time', time.time() - start)

        if n * f >= (1 + epsoid_p) * x:
            LB = n * f / (1 + epsoid_p)
            break

    alpha = math.sqrt(l * math.log(n) + math.log(2))
    beta = math.sqrt((1 - 1 / math.e) * (logcnk(n, k) + l * math.log(n) + math.log(2)))
    lambda_aster = 2 * n * pow(((1 - 1 / math.e) * alpha + beta), 2) * pow(epsoid, -2)
    theta = lambda_aster / LB
    length_r = len(R)
    diff = int(theta - length_r)

    if diff > 0:
        for _ in range(diff):
            v = random.randint(0, node_num - 1)
            rr = generate_rr(v, graph, node_num, model)
            R.append(rr)

    return R

def generate_rr(v, graph, node_num, model):
    if model == 'IC':
        return generate_rr_ic(v, graph)
    elif model == 'LT':
        return generate_rr_lt(v, graph)
    elif model == 'SI':
        return generate_rr_si(v, graph)

def node_selection(R, k, node_num):
    Sk = []
    rr_degree = [0 for _ in range(node_num)]
    node_rr_set = dict()
    matched_count = 0

    for j in range(len(R)):
        rr = R[j]
        for rr_node in rr:
            rr_degree[rr_node] += 1
            if rr_node not in node_rr_set:
                node_rr_set[rr_node] = list()
            node_rr_set[rr_node].append(j)

    for _ in range(k):
        max_point = rr_degree.index(max(rr_degree))
        Sk.append(max_point)
        matched_count += len(node_rr_set[max_point])
        index_set = list(node_rr_set[max_point])
        for jj in index_set:
            rr = R[jj]
            for rr_node in rr:
                rr_degree[rr_node] -= 1
                node_rr_set[rr_node].remove(jj)

    return Sk, matched_count / len(R)

def generate_rr_ic(node, graph):
    activity_set = [node]
    activity_nodes = [node]

    while activity_set:
        new_activity_set = []
        for seed in activity_set:
            for neighbor in graph.neighbors(seed):
                weight = graph.edges[seed, neighbor].get('weight', 1.0)
                if neighbor not in activity_nodes and random.random() < weight:
                    activity_nodes.append(neighbor)
                    new_activity_set.append(neighbor)
        activity_set = new_activity_set

    return activity_nodes

def generate_rr_lt(node, graph):
    activity_nodes = [node]
    activity_set = node

    while activity_set != -1:
        new_activity_set = -1
        neighbors = list(graph.neighbors(activity_set))
        if len(neighbors) == 0:
            break
        candidate = random.sample(neighbors, 1)[0]
        if candidate not in activity_nodes:
            activity_nodes.append(candidate)
            new_activity_set = candidate
        activity_set = new_activity_set

    return activity_nodes

def generate_rr_si(node, graph):
    activity_set = [node]
    activity_nodes = [node]

    while activity_set:
        new_activity_set = []
        for seed in activity_set:
            for neighbor in graph.neighbors(seed):
                if neighbor not in activity_nodes:
                    activity_nodes.append(neighbor)
                    new_activity_set.append(neighbor)
        activity_set = new_activity_set

    return activity_nodes

def logcnk(n, k):
    res = 0
    for i in range(n - k + 1, n + 1):
        res += math.log(i)
    for i in range(1, k + 1):
        res -= math.log(i)
    return res

def IMM(graph, config, seed_size, model):
    model = model.upper()
    l = 1
    epsoid = 0.5
    n = graph.number_of_nodes()
    k = seed_size
    l = l * (1 + math.log(2) / math.log(n))
    R = sampling(epsoid, l, graph, n, seed_size, model)
    Sk, z = node_selection(R, k, n)
    return Sk

####################

# diffusion models
def IC(g, config, seed, rounds=100):
    result = []

    for iter in range(rounds):

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

def LT(g, config, seed, rounds=100):
    result = []

    for iter in range(rounds):

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

# Zonghan's code
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
