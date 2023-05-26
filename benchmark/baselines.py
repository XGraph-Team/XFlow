import networkx as nx
import numpy as np
from simulation import simulationIC, simulationLT
#from score import SobolT
import ndlib
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
import statistics as s
# import heapdict as hd
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
# Function definition with inputs of a graph 'g', a configuration 'config', and a budget 'budget'
def celf(g, config, budget):

    # Initialize 'selected' as an empty list. This list will eventually hold the selected nodes
    selected = []
    
    # Get a list of all nodes in the graph 'g'
    candidates = list(g.nodes())

    # Initialize 'gains' as an empty list. This list will hold the gain of each node
    gains = []

    # For each node in the list of candidates
    for node in candidates:
        # Create a new list 'seed' that includes all currently selected nodes plus the current node
        seed = selected + [node]
        
        # Run the IC function on the graph with the 'seed' list and get the result
        result = IC(g, config, seed)
        
        # Calculate the average (mean) of the result and assign it to 'gain'
        gain = s.mean(result)
        
        # Add a tuple of negative 'gain' and 'node' to the 'gains' list
        heapq.heappush(gains, (-gain, node))

    # Repeat the next steps 'budget' times
    for i in range(budget):
        # Keep looping until a condition is met
        while True:
            # Get the tuple with the highest gain (which will be the first in the list due to the sorting in the heap)
            gain, node = heapq.heappop(gains)
            
            # Again, create a new list 'seed' that includes all currently selected nodes plus the current node
            seed = selected + [node]
            
            # Run the IC function on the graph with the 'seed' list and get the result
            result = IC(g, config, seed)
            
            # Calculate the average (mean) of the result and assign it to 'new_gain'
            new_gain = s.mean(result)
            
            # If 'new_gain' equals the negation of 'gain'
            if new_gain == -gain:
                # Break the loop
                break
            else:
                # Otherwise, add the tuple of negative 'new_gain' and 'node' back to the 'gains' list
                heapq.heappush(gains, (-new_gain, node))

        # Append the current node to the 'selected' list
        selected.append(node)
        
        # Remove the current node from the 'candidates' list
        candidates.remove(node)
        print(sorted(selected))

    # Return the list of selected nodes
    return (sorted(selected))

def celf2(g, config, budget):   
    """
    Inputs: g:     Network graph
            config: Configuration object for the IC model
            budget:     Size of seed set
    Return: A seed set of nodes as an approximate solution to the IM problem
    """
      
    # --------------------
    # Find the first node with greedy algorithm
    # --------------------
    
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

# baseline 9.2 CELFPP
# Function definition with inputs of a graph 'g', a configuration 'config', and a budget 'budget'
def celfpp(g, config, budget):

    # Initialize 'selected' as an empty list. This list will eventually hold the selected nodes
    selected = []
    
    # Get a list of all nodes in the graph 'g'
    candidates = list(g.nodes())

    # Initialize 'gains' as an empty list. This list will hold the gain of each node
    gains = []

    # For each node in the list of candidates
    for node in candidates:
        # Create a new list 'seed' that includes all currently selected nodes plus the current node
        seed = selected + [node]
        
        # Run the IC function on the graph with the 'seed' list and get the result
        result = IC(g, config, seed)
        
        # Calculate the average (mean) of the result and assign it to 'gain'
        gain = s.mean(result)
        
        # Add a tuple of negative 'gain', 'node', and 'None' (which will later be replaced with the last seed added) to the 'gains' list
        heapq.heappush(gains, (-gain, node, None))

    # Initialize 'last_seed' as 'None'. This variable will hold the last seed that was added to 'selected'
    last_seed = None

    # Repeat the next steps 'budget' times
    for i in range(budget):
        # Keep looping until a condition is met
        while True:
            # Get the tuple with the highest gain (which will be the first in the list due to the sorting in the heap)
            gain, node, last_added_seed = heapq.heappop(gains)

            # If 'last_added_seed' equals 'last_seed'
            if last_added_seed == last_seed:
                # Then the gain doesn't need to be recomputed, so set 'new_gain' to the negation of 'gain'
                new_gain = -gain
            else:
                # Otherwise, create a new list 'seed' that includes all currently selected nodes plus the current node
                seed = selected + [node]
                
                # Run the IC function on the graph with the 'seed' list and get the result
                result = IC(g, config, seed)
                
                # Calculate the average (mean) of the result and assign it to 'new_gain'
                new_gain = s.mean(result)

            # If 'new_gain' equals the negation of 'gain'
            if new_gain == -gain:
                # Break the loop
                break
            else:
                # Otherwise, add the tuple of negative 'new_gain', 'node', and 'last_seed' back to the 'gains' list
                heapq.heappush(gains, (-new_gain, node, last_seed))

        # Append the current node to the 'selected' list
        selected.append(node)
        
        # Remove the current node from the 'candidates' list
        candidates.remove(node)
        
        # Set 'last_seed' to the current node
        last_seed = node

    # Print the sorted list of selected nodes
    print(sorted(selected))
    
    # Return the list of selected nodes
    return selected

def celfpp2(g, config, budget):   
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

    """
    Inputs: g:     Network graph
            config: Configuration object for the IC model
            budget:     Size of seed set
    Return: A seed set of nodes as an approximate solution to the IM problem
    """
      
    # Compute marginal gain for each node
    candidates = list(g.nodes())

    # Initialize the gains list as a min heap for efficiency
    gains = []

    # For each candidate node, compute its marginal gain and push it into the heap along with the node itself
    for node in candidates:
        gain = s.mean(IC(g, config, [node]))
        heapq.heappush(gains, (-gain, node, None)) # Initial last added seed is None

    # Track the last added seed node
    last_seed = None

    # Select the first node and remove from candidate list
    selected = []

    # Repeat the next steps 'budget' times
    for _ in range(budget):
        while True:
            # Pop the node with highest gain from heap
            gain, node, last_added_seed = heapq.heappop(gains)
            
            # Check if the gain needs to be updated
            if last_added_seed == last_seed: # If the last added seed hasn't changed
                new_gain = -gain # No need to recompute gain
            else:
                # Otherwise, recompute the gain
                new_gain = s.mean(IC(g, config, selected+[node])) 

            # If the recomputed gain remains the same, break the loop
            if new_gain == -gain:
                break
            else:
                # Otherwise, push the node with its new gain into the heap
                heapq.heappush(gains, (-new_gain, node, last_seed)) # Update last added seed

        # Append the current node to the 'selected' list
        selected.append(node)
        # Remove the current node from the 'candidates' list
        candidates.remove(node)
        # Update the last seed added
        last_seed = node
        print(sorted(selected))
    
    return sorted(selected)


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
    print(sorted(selected))

    return selected

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
