import networkx as nx
import numpy as np
from simulation import simulationIC, simulationLT
import ndlib
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
import statistics as s
import random
import heapq
import matplotlib.pyplot as plt
from random import uniform, seed
import numpy as np
import pandas as pd
import time
from igraph import *
# import random
from collections import Counter
import operator
import numpy as np
import copy

# random

# baselines: simulation based

# greedy
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
    print(sorted(selected))

    return selected

def celf(g, config, budget):   
    """
    Inputs: g:     Network graph
            config: Configuration object for the IC model
            budget:     Size of seed set
    Return: A seed set of nodes as an approximate solution to the IM problem
    """
      
    # Find the first node with greedy algorithm
    
    # Compute marginal gain for each node
    candidates = list(g.nodes())
    #, start_time = list(g.nodes()), time.time()
    # step 1, call our IC function, get the result of list
    # step 2, calculate the margin gain 
    marg_gain = [s.mean(IC(g, config, [node])) for node in candidates]

    # Create the sorted list of nodes and their marginal gain 
    Q = sorted(zip(candidates,marg_gain), key = lambda x: x[1],reverse=True)

    # Select the first node and remove from candidate list
    selected, spread, Q = [Q[0][0]], Q[0][1], Q[1:]
    # timelapse = [time.time() - start_time]
    
    # Find the next budget-1 nodes using the CELF list-sorting procedure
    
    for _ in range(budget-1):    

        check = False      
        while not check:
            
            # Recalculate spread of top node
            current = Q[0][0]
            
            # Evaluate the spread function and store the marginal gain in the list
            Q[0] = (current, s.mean(IC(g, config, selected+[current])) - spread)

            # Re-sort the list
            Q = sorted(Q, key = lambda x: x[1], reverse=True)

            # Check if previous top node stayed on top after the sort
            check = Q[0][0] == current

        # Select the next node
        selected.append(Q[0][0])
        spread = Q[0][1]
        # timelapse.append(time.time() - start_time)
        
        # Remove the selected node from the list
        Q = Q[1:]
        print(sorted(selected))
    
    return(sorted(selected))
    # return(sorted(S),timelapse)

def celfpp(g, config, budget):   
    """
    Inputs: g:     Network graph
            config: Configuration object for the IC model
            budget:     Size of seed set
    Return: A seed set of nodes as an approximate solution to the IM problem
    """
      
    # Compute marginal gain for each node
    candidates = list(g.nodes())
    marg_gain = [s.mean(IC(g, config, [node])) for node in candidates]

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
                new_gain = s.mean(IC(g, config, selected+[current])) - spread
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

        print(sorted(selected))

    return sorted(selected)

# greedy with IC
# def greedyIC(g, config, budget):

#     selected = []
#     candidates = []

#     for node in g.nodes():
#         candidates.append(node)

#     for i in range(budget):
#         max = 0
#         index = -1
#         for node in candidates:
#             seed = []
#             for item in selected:
#                 seed.append(item)
#             seed.append(node)

#             # g_temp = g.__class__()
#             # g_temp.add_nodes_from(g)
#             # g_temp.add_edges_from(g.edges)
#             result = []

#             for iter in range(100):

#                 model_temp = ep.IndependentCascadesModel(g) # _temp
#                 config_temp = mc.Configuration()
#                 config_temp.add_model_initial_configuration('Infected', seed)

#                 for a, b in g.edges(): # _temp
#                     weight = config.config["edges"]['threshold'][(a, b)]
#                     # g_temp[a][b]['weight'] = weight
#                     config_temp.add_edge_configuration('threshold', (a, b), weight)

#                 model_temp.set_initial_status(config_temp)

#                 iterations = model_temp.iteration_bunch(5)

#                 total_no = 0

#                 for j in range(5):
#                     a = iterations[j]['node_count'][1]
#                     total_no += a

#                 result.append(total_no)

#             if s.mean(result) > max:
#                 max = s.mean(result)
#                 index = node

#         selected.append(index)
#         candidates.remove(index)

#     return selected

# greedy with LT
# def greedyLT(g, config, budget):

#     selected = []
#     candidates = []

#     for node in g.nodes():
#         candidates.append(node)

#     for i in range(budget):
#         max = 0
#         index = -1
#         for node in candidates:
#             seed = []
#             for item in selected:
#                 seed.append(item)
#             seed.append(node)

#             # g_temp = g.__class__()
#             # g_temp.add_nodes_from(g)
#             # g_temp.add_edges_from(g.edges)
#             result = []

#             for iter in range(100):

#                 model_temp = ep.ThresholdModel(g) # _temp
#                 config_temp = mc.Configuration()
#                 config_temp.add_model_initial_configuration('Infected', seed)

#                 for a, b in g.edges(): # _temp
#                     weight = config.config["edges"]['threshold'][(a, b)]
#                     # g_temp[a][b]['weight'] = weight
#                     config_temp.add_edge_configuration('threshold', (a, b), weight)

#                 for i in g.nodes():
#                     threshold = random.randrange(1, 20)
#                     threshold = round(threshold / 100, 2)
#                     config_temp.add_node_configuration("threshold", i, threshold)

#                 model_temp.set_initial_status(config_temp)

#                 iterations = model_temp.iteration_bunch(5)

#                 total_no = iterations[4]['node_count'][1]
#                 result.append(total_no)

#             if s.mean(result) > max:
#                 max = s.mean(result)
#                 index = node

#         selected.append(index)
#         candidates.remove(index)

#     return selected

# CELF with heapq implementation
# Function definition with inputs of a graph 'g', a configuration 'config', and a budget 'budget'
# def celf_heapq(g, config, budget):

#     # Initialize 'selected' as an empty list. This list will eventually hold the selected nodes
#     selected = []
    
#     # Get a list of all nodes in the graph 'g'
#     candidates = list(g.nodes())

#     # Initialize 'gains' as an empty list. This list will hold the gain of each node
#     gains = []

#     # For each node in the list of candidates
#     for node in candidates:
#         # Create a new list 'seed' that includes all currently selected nodes plus the current node
#         seed = selected + [node]
        
#         # Run the IC function on the graph with the 'seed' list and get the result
#         result = IC(g, config, seed)
        
#         # Calculate the average (mean) of the result and assign it to 'gain'
#         gain = s.mean(result)
        
#         # Add a tuple of negative 'gain' and 'node' to the 'gains' list
#         heapq.heappush(gains, (-gain, node))

#     # Repeat the next steps 'budget' times
#     for i in range(budget):
#         # Keep looping until a condition is met
#         while True:
#             # Get the tuple with the highest gain (which will be the first in the list due to the sorting in the heap)
#             gain, node = heapq.heappop(gains)
            
#             # Again, create a new list 'seed' that includes all currently selected nodes plus the current node
#             seed = selected + [node]
            
#             # Run the IC function on the graph with the 'seed' list and get the result
#             result = IC(g, config, seed)
            
#             # Calculate the average (mean) of the result and assign it to 'new_gain'
#             new_gain = s.mean(result)
            
#             # If 'new_gain' equals the negation of 'gain'
#             if new_gain == -gain:
#                 # Break the loop
#                 break
#             else:
#                 # Otherwise, add the tuple of negative 'new_gain' and 'node' back to the 'gains' list
#                 heapq.heappush(gains, (-new_gain, node))

#         # Append the current node to the 'selected' list
#         selected.append(node)
        
#         # Remove the current node from the 'candidates' list
#         candidates.remove(node)
#         print(sorted(selected))

#     # Return the list of selected nodes
#     return (sorted(selected))

# CELFPP with heapq implementation
# Function definition with inputs of a graph 'g', a configuration 'config', and a budget 'budget'
# def celfpp_heapq(g, config, budget):

#     # Initialize 'selected' as an empty list. This list will eventually hold the selected nodes
#     selected = []
    
#     # Get a list of all nodes in the graph 'g'
#     candidates = list(g.nodes())

#     # Initialize 'gains' as an empty list. This list will hold the gain of each node
#     gains = []

#     # For each node in the list of candidates
#     for node in candidates:
#         # Create a new list 'seed' that includes all currently selected nodes plus the current node
#         seed = selected + [node]
        
#         # Run the IC function on the graph with the 'seed' list and get the result
#         result = IC(g, config, seed)
        
#         # Calculate the average (mean) of the result and assign it to 'gain'
#         gain = s.mean(result)
        
#         # Add a tuple of negative 'gain', 'node', and 'None' (which will later be replaced with the last seed added) to the 'gains' list
#         heapq.heappush(gains, (-gain, node, None))

#     # Initialize 'last_seed' as 'None'. This variable will hold the last seed that was added to 'selected'
#     last_seed = None

#     # Repeat the next steps 'budget' times
#     for i in range(budget):
#         # Keep looping until a condition is met
#         while True:
#             # Get the tuple with the highest gain (which will be the first in the list due to the sorting in the heap)
#             gain, node, last_added_seed = heapq.heappop(gains)

#             # If 'last_added_seed' equals 'last_seed'
#             if last_added_seed == last_seed:
#                 # Then the gain doesn't need to be recomputed, so set 'new_gain' to the negation of 'gain'
#                 new_gain = -gain
#             else:
#                 # Otherwise, create a new list 'seed' that includes all currently selected nodes plus the current node
#                 seed = selected + [node]
                
#                 # Run the IC function on the graph with the 'seed' list and get the result
#                 result = IC(g, config, seed)
                
#                 # Calculate the average (mean) of the result and assign it to 'new_gain'
#                 new_gain = s.mean(result)

#             # If 'new_gain' equals the negation of 'gain'
#             if new_gain == -gain:
#                 # Break the loop
#                 break
#             else:
#                 # Otherwise, add the tuple of negative 'new_gain', 'node', and 'last_seed' back to the 'gains' list
#                 heapq.heappush(gains, (-new_gain, node, last_seed))

#         # Append the current node to the 'selected' list
#         selected.append(node)
        
#         # Remove the current node from the 'candidates' list
#         candidates.remove(node)
        
#         # Set 'last_seed' to the current node
#         last_seed = node

#     # Print the sorted list of selected nodes
#     print(sorted(selected))
    
#     # Return the list of selected nodes
#     return selected


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

# https://github.com/Braylon1002/IMTool
# IMRank



def IMRank(g, config, budget):
    """
    IMRank algorithm to rank the nodes based on their influence.
    """

    # Obtain adjacency matrix from the graph
    adjacency_matrix = nx.adjacency_matrix(g).todense()
    
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
        
    # elapsed_time = time.perf_counter() - start
    # print(f"Elapsed time: {elapsed_time} seconds")

    # Select top nodes up to the budget
    selected = r[:budget]
    print(sorted(selected))
    return selected


# baselines: sketch based
# todo
# https://github.com/Braylon1002/IMTool
#RIS

def RIS(g, config, budget):
    mc=2
    start_time = time.time()
    R = [get_RRS(g, config) for _ in range(mc)]

    SEED = []
    timelapse = []
    for _ in range(budget):
        # Collect all nodes from all RRS
        flat_map = [item for subset in R for item in subset]
        # Only proceed if there are nodes in the flat_map
        if flat_map:
            seed = Counter(flat_map).most_common()[0][0]
            print(Counter(flat_map).most_common()[0])
            SEED.append(seed)

            R = [rrs for rrs in R if seed not in rrs]

        timelapse.append(time.time() - start_time)

    return (sorted(SEED), timelapse)


# helpers
# helper function for IMRank
def LFA(matrix):
    """
    Linear Feedback Algorithm to update the ranks of the nodes.
    """
    n = len(matrix)
    Mr = [1 for i in range(n)]
    for i_ in range(1, n):
        i = n - i_
        for j in range(0, i + 1):
            Mr[j] = Mr[j] + matrix[j][i] * Mr[i]
            Mr[i] = (1 - matrix[j][i]) * Mr[i]
    return Mr

# helper function for RIS
def get_RRS(g, config):
    """
    Inputs: g: Network graph
            config: Configuration object for the IC model
    Outputs: A random reverse reachable set expressed as a list of nodes
    """
    # select a random node as the starting point
    source = random.choice(list(g.nodes()))
    
    # get edges according to the propagation probability
    edges = [(u, v) for (u, v, d) in g.edges(data=True) if uniform(0, 1) < config.config["edges"]['threshold'][(u, v)]]
    
    # create a subgraph based on the edges
    g_sub = g.edge_subgraph(edges)
    
    # perform a depth-first traversal from the source node to get the RRS
    RRS = list(nx.dfs_preorder_nodes(g_sub, source))
    return RRS

# diffusion models
# fixme set MC = 100
def IC(g, config, seed):
    # number of Monte Carlo simulations to be run for the IC model
    mc_number = 2
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
