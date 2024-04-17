#!/usr/bin/env python
# coding: utf-8

# ### Necessary imports

# In[1]:


import xflow
from xflow.util import run
import cosasi
import networkx as nx
from xflow.dataset.nx import connSW
import random
import numpy as np
from torch_geometric.data.data import Data
from networkx import Graph


# ### Setup
# Initializes graph and SIR parameters.

# In[2]:


def setup(graph_size, graph_beta, infection_beta, gamma):
    (g, config) = connSW(n=graph_size, beta=graph_beta)
    s = random.sample(list(g.nodes()), k=random.randint(1,10))

    """
    SIR Parameters:
    beta = infection rate
    gamma = recovery rate
    """
    if infection_beta is None:
        infection_beta = random.uniform(0.1,0.6)
        
    if gamma is None:
        gamma = random.uniform(0.1,0.3)

    diameter = nx.diameter(g)
    
    return g,s,infection_beta,gamma,diameter


# ### SIR Simulation Functions
# The following functions simulate SIR from t=0 to t=diameter. Notably, there are three seperate functions depending on the output type desired for observations. This allows us to store the values in their desired output during the running of the simulation, avoiding the need for conversions after the simulation is over. However, if Dr. Chen dislikes this setup for the simulation functions, we can change it to run everything in a single function and then convert to the user's desired output type for observations after the simulation ends. Descriptions of the desired output types can be found further below.

# In[3]:


#simulate with observations stored in numpy array
def simulate_np(g, s, beta, gamma, diameter):
    node_states = []
    #initializing every node as susceptible
    for node in g.nodes():
        node_states.append('Susceptible')
    #initializing every node in seed node as infected
    for seed_node in s:
        node_states[seed_node] = 'Infected'
           
    node_states = np.array(node_states)
    
    snapshots = []
    #add original states to snapshots
    snapshot = {
        'time' : 0,
        'observation' : node_states.copy()  
    }
    snapshots.append(snapshot)
        
    #run simulation until diameter of graph
    for _ in range(diameter):
        snapshot = simulation_step_np(g, node_states, beta, gamma, _)
        node_states = snapshot['observation'].copy()
        snapshots.append(snapshot)
       
    return snapshots


def simulation_step_np(g, node_states, beta, gamma, _):
    #simulating diffusion process for one step
    new_states = np.copy(node_states)
    
    for node in g.nodes():
        if node_states[node] == 'Infected':
            for neighbor in g.neighbors(node):
                if node_states[neighbor] == 'Susceptible' and random.random() < beta:
                    new_states[neighbor] = 'Infected'
            
            if random.random() < gamma:
                new_states[node] = 'Recovered'
    
    snapshot = {
        'time' : _ + 1,
        'observation' : new_states
    }
    
    return snapshot


# In[4]:


#simulate with observations stored as attributes to networkx graph
def simulate_nx(g, s, beta, gamma, diameter):
    #initializing every node as susceptible
    nx.set_node_attributes(g, 'Susceptible', name='state')
    #initializing every node in seed node as infected
    for seed_node in s:
        g.nodes[seed_node]['state'] = 'Infected'
    
    snapshots = []
    #add original states to snapshots
    snapshot = {
        'time' : 0,
        'observation' : g.copy()
    }
    snapshots.append(snapshot)
    
    #run simulation until diameter of graph
    for _ in range(diameter):
        snapshot = simulation_step_nx(g, beta, gamma, _)
        g = snapshot['observation'].copy()
        snapshots.append(snapshot)
        
    return snapshots


def simulation_step_nx(g, beta, gamma, _):
    #simulating diffusion process for one step
    
    for node in g.nodes():
        if g.nodes[node]['state'] == 'Infected':
            for neighbor in g.neighbors(node):
                if g.nodes[neighbor]['state'] == 'Susceptible' and random.random() < beta:
                    g.nodes[neighbor]['state'] = 'Infected'
            
            if random.random() < gamma:
                g.nodes[node]['state'] = 'Recovered'
                
    snapshot = {
        'time' : _ + 1,
        'observation' : g
    } 
    
    return snapshot


# In[5]:


#simulate with observations stored as attributes to pytorch geometric data object
def simulate_torch(g, s, beta, gamma, diameter):
    from torch_geometric.utils.convert import from_networkx
    #initializing every node as susceptible
    nx.set_node_attributes(g, 0, name='state') #0 = 'susceptible', 1='infected',2='recovered'
    #initializing every node in seed node as infected
    for seed_node in s:
        g.nodes[seed_node]['state'] = 1
    
    snapshots = []
    #add original states to snapshots
    snapshot = {
        'time' : 0,
        'observation' : from_networkx(g.copy())
    }
    snapshots.append(snapshot)
    
    #run simulation until diameter of graph
    for _ in range(diameter):
        snapshot = simulation_step_torch(g, beta, gamma, _)
        g = snapshot['observation']
        snapshot['observation'] = from_networkx(g.copy())
        snapshots.append(snapshot)
        
    return snapshots


def simulation_step_torch(g, beta, gamma, _):
    #from torch_geometric.utils.convert import from_networkx
    #simulating diffusion process for one step
    
    for node in g.nodes():
        if g.nodes[node]['state'] == 1:
            for neighbor in g.neighbors(node):
                if g.nodes[neighbor]['state'] == 0 and random.random() < beta:
                    g.nodes[neighbor]['state'] = 1
            
            if random.random() < gamma:
                g.nodes[node]['state'] = 2
                
    snapshot = {
        'time' : _ + 1,
        'observation' : g
    } 
    
    return snapshot


# ### Run_sim helper function
# run_sim() is a helper function called by both forwards and backwards. If the user did not give a lower interval, it chooses one randomly. Then, it runs the simulation from lower_interval to lower_interval+distance. If lower_interval+distance is less than the diameter of the graph, then the simulation will stop early, avoiding extra computation. The function returns all results from interval 0 to interval_lower+distance, so that forwards and backwards can choose the respective intervals they need to save.

# In[6]:


def run_sim(distance, interval_lower, obs_type, g, s, beta, gamma, diameter):
    dist_max = max(distance)
    
    r = interval_lower
    if r < 0:
        r = random.randrange(diameter-dist_max) #choose random timesteps
    
    # throw possible errors
    if (r < 0) or (r + dist_max > diameter):
        raise Exception('Distance is too large for graph settings given.')
        
    #run the simulation
    if obs_type == 'numpy':
        simulation_result = simulate_np(g, s, beta, gamma, r + dist_max)
    elif obs_type == 'networkx':
        simulation_result = simulate_nx(g, s, beta, gamma, r + dist_max)
    elif obs_type == 'torch':
        simulation_result = simulate_torch(g, s, beta, gamma, r + dist_max)
    else:
        raise Exception("Acceptable values for obs_storage are: 'numpy', 'networkx', 'torch' ")
        
    return simulation_result


# ### Forwards and Backwards Tasks
# Generates sets of random graph observations. Forwards returns observations at i, i+distance. Backwards returns observations at i, i-distance.
# 
# - Distance - distance between graph observations. Can be int or an array/list of int.
# - interval_lower - (optional) If given, all pairs of observations will have a lower time interval of this value. Otherwise, all intervals will start at a randomly chosen time interval.
# - num_results - Number of pairs of observations to generate. Default is 10.
# - obs_storage - Data type of observations. Default is 'numpy'.
#     - 'numpy' - states stored in a numpy array, seperate from the graph.
#     - 'networkx' - states stored as attributes of the networkx graph.
#     - 'torch' - states stored as integer attributes of a pytorch geometric data object.
# - graph_size - Size of graphs randomly generated with connSW(). Default is 1000.
# - graph_beta - Beta value of graphs randomly generated with connSW(). Default is 0.1.
# - infection_beta - Beta value for SIR simulation. If None, setup sets it equal to random.uniform(0.1,0.6).
# - gamma - Gamma value for SIR simulation. If None, setup sets it equal to random.uniform(0.1,0.3).

# In[22]:


def forward(distance, interval_lower = -1, num_results=10, obs_type = 'numpy', graph_size=1000, graph_beta = 0.1, infection_beta = None, infection_gamma = None):
    if isinstance(distance,int):
        distance = [distance]
    
    #generate results
    results = []
    for n in range(num_results):
        (g,s,beta,gamma,diameter) = setup(graph_size, graph_beta, infection_beta, infection_gamma)
        simulation_result = run_sim(distance, interval_lower, obs_type, g, s, beta, gamma, diameter)
        
        intervals =[len(simulation_result) - 1 -max(distance)]
        for d in distance:
            intervals.append(intervals[0] + d)
            
        #append two results that are distance apart
        results.append({'observations': [simulation_result[t] for t in intervals], 
                        'base_graph': g, 
                        'SIR_model': {'beta':beta,'gamma':gamma}})
        
    
    return results

def backward(distance, interval_lower = -1, num_results=10, obs_type = 'numpy', graph_size=1000, graph_beta = 0.1, infection_beta = None, infection_gamma = None):  
    if isinstance(distance,int):
        distance = [distance]
    
    #generate results
    results = []
    for n in range(num_results):
        (g,s,beta,gamma,diameter) = setup(graph_size, graph_beta, infection_beta, infection_gamma)
        simulation_result = run_sim(distance, interval_lower, obs_type, g.copy(), s, beta, gamma, diameter)
        
        intervals =[len(simulation_result) - 1]
        for d in distance:
            intervals.append(intervals[0] - d)
            
        #append observations, the starting graph, the starting SIR model
        results.append({'observations': [simulation_result[t] for t in intervals], 
                        'base_graph': g, 
                        'SIR_model': {'beta':beta,'gamma':gamma}})
        
    return results 


# ### Evaluation Metrics
# 'Infected' or 1 state is treated as positive, 'Susceptible' or 0 and 'Recovered' or 2 are treated as negative. Observations can be in the form of a list/numpy array of values, networkx graph, or pytorch geometric data object.

# In[13]:


def to_SI_obs(obs):
    if isinstance(obs, Graph):
        obs_np = np.array(list(nx.get_node_attributes(obs, 'state').values()))
    elif isinstance(obs, Data):
        obs_np = np.array(obs.to_dict()['state'].tolist())
        return obs_np
    else:
        obs_np = obs
        
    l = len(obs_np)
    SI = np.zeros(l)
    for i in range(l):
        if obs_np[i] == 'Infected':
            SI[i] = 1
        if obs_np[i] == 'Recovered':
            SI[i] = 2
            
    return SI

def graph_eval(obs_true, obs_pred):
    y = to_SI_obs(obs_true)
    y_pred = to_SI_obs(obs_pred)
    
    # Initialize Empty Matrix
    conf_mat = { 'TP':0, 'FP':0, 'TN':0, 'FN':0 }
    
    for i in range( len( y ) ):
        
        # TP
        if y[i] == 1 and y_pred[i] == 1:
            conf_mat['TP'] += 1
            
        # FN
        elif y[i] == 1 and y_pred[i] in [0,2]:
            conf_mat['FN'] += 1
            
        # FP
        elif y[i] in [0,2] and y_pred[i] == 1:
            conf_mat['FP'] += 1
            
        # TN
        elif y[i] in [0,2] and y_pred[i] in [0,2]:
            conf_mat['TN'] += 1
            
    eval_metrics = {'precision':0,'recall':0, 'f1':0}
    
    eval_metrics['precision'] = conf_mat['TP']/(conf_mat['TP']+conf_mat['FP'])
    eval_metrics['recall'] = conf_mat['TP']/(conf_mat['TP']+conf_mat['FN'])
    eval_metrics['f1'] = (2*eval_metrics['precision']*eval_metrics['recall'])/(1e-8 + eval_metrics['precision'] + eval_metrics['recall'])
    
    return eval_metrics
