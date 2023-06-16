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
from xflow.diffusion.SI import SI
from xflow.diffusion.IC import IC
from xflow.diffusion.LT import LT

# random

# baselines: simulation based

# greedy
def greedy(g, config, budget, rounds=100, model='SI', beta=0.1):

    selected = []
    candidates = list(g.nodes())

    for i in range(budget):

        max = 0
        index = -1
        for node in candidates:
            seeds = selected + [node]

            if (model == "IC"):
                result = IC(g, config, seeds, rounds)
            elif (model == "LT"):
                result = LT(g, config, seeds, rounds)
            elif (model == "SI"):
                result = SI(g, config, seeds, rounds, beta)
            
            if s.mean(result) > max:
                max = s.mean(result)
                index = node

        selected.append(index)
        candidates.remove(index)

    print(selected)
    return selected

def celf(g, config, budget, rounds=100, model='SI', beta=0.1): 
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

def celfpp(g, config, budget, rounds=100, model='SI', beta=0.1):

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
        B = A[:, nodes]
        b = B * u[nodes]

        score = v - 2 * b * u
        score[nodes] = -1

        nodes.append(np.argmax(score))

    print(nodes)
    return nodes

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

# def IMM(g, config, budget, rounds=100, model='SI', beta=0.1):
#     l = 1
#     epsilon = 0.1
#     l = l * (1 + np.log(2) / np.log(len(g.nodes()))) # Update l
#     k = budget
    
#     R = Sampling(g, config, epsilon, l, model, rounds, beta)
    
#     S = NodeSelection(R, k)
#     print(S)
#     return S

# def Sampling(g, config, epsilon, l, model='SI', rounds=100, beta=0.1):
#     R = []
#     n = len(g.nodes())
#     LB = 1
#     eps_prime = np.sqrt(2) * epsilon
#     for i in range(1, int(np.log2(n))):
#         x = n / (2 ** i)
#         theta_i = (l / eps_prime ** 2) * np.log(n) / x
#         while len(R) <= theta_i:
#             v = random.choice(list(g.nodes()))
#             R.append(get_RRS(g, config))
#         S_i = NodeSelection(R, int(x))  # Changed budget to int(x) here
#         if n * len(S_i) >= (1 + eps_prime) * x:  
#             LB = n * len(S_i) / (1 + eps_prime)
#             break
#     theta = (l / (epsilon ** 2)) * np.log(n) / LB
#     while len(R) <= theta:
#         v = random.choice(list(g.nodes()))
#         R.append(get_RRS(g, config))
#     return R

# def NodeSelection(R, k):
#     S = []
#     RR_sets_covered = set()
#     for _ in range(k):
#         max_spread = 0
#         best_node = None
#         for v in set().union(*R):  
#             if v not in S:
#                 RR_sets_can_cover = sum([v in RR for RR in R if tuple(RR) not in RR_sets_covered])
#                 if RR_sets_can_cover > max_spread:
#                     max_spread = RR_sets_can_cover
#                     best_node = v
#         if best_node is not None:
#             S.append(best_node)
#             RR_sets_covered |= set([tuple(RR) for RR in R if best_node in RR])
#         else:
#             print("No suitable node found!")
#     return S


# updates to the Mr vector occur simultaneously:
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


def get_RRS(g, config):
    """
    Inputs: g: Network graph
            config: Configuration object for the IC model
    Outputs: A random reverse reachable set expressed as a list of nodes
    """
    # get edges according to the propagation probability
    edges = [(u, v) for (u, v, d) in g.edges(data=True) if uniform(0, 1) < config.config["edges"]['threshold'][(u, v)]]
    
    # create a subgraph based on the edges
    g_sub = g.edge_subgraph(edges)
    
    # select a random node as the starting point that is part of the subgraph
    source = random.choice(list(g_sub.nodes()))
    
    # perform a depth-first traversal from the source node to get the RRS
    RRS = list(nx.dfs_preorder_nodes(g_sub, source))
    return RRS

