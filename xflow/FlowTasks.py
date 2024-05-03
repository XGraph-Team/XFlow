# pip dependencies
#!pip install torch
#!pip install torch_geometric==2.2.0
#!pip install xflow-net==0.0.21
#!pip install networkx
#!pip install ndlib
#!pip install pyg_lib torch_scatter torch_sparse torch_cluster torch_spline_conv -f https://data.pyg.org/whl/torch-2.2.0+cpu.html
#!pip install torch_geometric_temporal

# group 1
import numpy as np
import random
import networkx as nx
from networkx import Graph
from torch_geometric.data.data import Data, torch
import xflow
from xflow.dataset.nx import connSW
from xflow.FlowTasks import forward, backward, graph_eval 
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
import warnings
from torch_geometric.utils.convert import from_networkx
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

def connSW(n, beta=None):
    g = nx.connected_watts_strogatz_graph(n, 10, 0.1) #Generate connSW graph

    config = mc.Configuration()

    #add edge weights in ndlib config
    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        if beta:
            weight = beta
        g[a][b]['weight'] = weight
        config.add_edge_configuration("threshold", (a, b), weight)

    return g, config

def BA(n=1000, beta=None):
    g = nx.barabasi_albert_graph(n, 5)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        if beta:
            weight = beta
        g[a][b]['weight'] = weight
        config.add_edge_configuration("threshold", (a, b), weight)

    return g, config

def ER(n=5000, beta=None):
    g = nx.erdos_renyi_graph(n, 0.1)

    while nx.is_connected(g) == False:
        g = nx.erdos_renyi_graph(n, 0.1)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        if beta:
            weight = beta
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

graph_gen_dict = {'connSW':connSW, 'BA':BA, 'ER':ER} #dictionary of string to graph gen mappings, shpuld be a generator that
                                                     #returns g as networkx grapg and config as ndlib config
                                                     #and accepts values of n (nodes) and beta (edge weight override)

def setup(graph_kind, graph_size, graph_beta, inf_beta, inf_gamma, inf_initial_frac):

    #generate a graph
    for name, gen_function in graph_gen_dict.items():
        if name == graph_kind:
            (g, config) = gen_function(n=graph_size, beta=graph_beta)
            break
    #make sure graph gen was sucessful
    if g is None:
        raise Exception('Graph generation function not known.')

    #sir model setup
    if inf_beta is None:
        inf_beta = random.uniform(0.01,0.06)
    if inf_gamma is None:
        inf_gamma = random.uniform(0.005,0.03)
    if inf_initial_frac is None:
        inf_initial_frac = random.uniform(0.02,0.05)

    config.add_model_parameter('beta', inf_beta)
    config.add_model_parameter('gamma', inf_gamma)
    config.add_model_parameter("fraction_infected", inf_initial_frac)

    model = ep.SIRModel(g)
    model.set_initial_status(config)

    return g,model,config

def run_sim(distance, interval_lower, g, model):
    #choose timesteps, dont run longer than needed
    diameter = nx.diameter(g)
    dist_max = max(distance)
    r = interval_lower
    if r < 0:
        if (diameter-dist_max <0):
            warnings.warn(f'Distance of {dist_max} exceeds graph diameter of {diameter}.')
            diameter = dist_max
        if (diameter-dist_max ==0):
            r=0
        else:
            r = random.randrange(diameter-dist_max) #choose random timesteps


    #run the simulation
    iterations = model.iteration_bunch(r+dist_max+1, node_status=True)

    node_states_iterations = []
    node_states = {}
    for iteration in iterations:
        if iteration['iteration'] == 0:
            node_states = {node: status for node, status in iteration['status'].items()}
        else:
            for node, status in iteration['status'].items():
                node_states[node] = status
        node_states_iterations.append(node_states.copy())
    #print(node_states_iterations)
    return node_states_iterations


def format_sim_result(intervals, iterations, obs_type, g):
    simulation_result = []
    if obs_type == 'numpy':
        #get result at each timestep
        for interval in intervals:
            node_states = iterations[interval]

            obs = np.array(list(node_states.values()))
            #build the snapshot using the observation at this iteration
            snapshot = {
                'time' : interval,
                'observation' : obs
            }
            #append the snapshot to sim result
            simulation_result.append(snapshot)

        return simulation_result


    if obs_type == 'torch' or obs_type == 'networkx':
        start = intervals[0]
        node_states = iterations[start]
        #node_states = {node: status for node, status in iteration['status'].items()}
        nx.set_node_attributes(g, node_states, name = 'state_x')
        nx.set_node_attributes(g, start, name = 'time_x')

        #get result at each timestep
        simulation_result = []
        for interval in intervals[1:]:
            node_states = iterations[interval]
            #node_states = {node: status for node, status in iteration['status'].items()}

            if obs_type == 'networkx':
                nx.set_node_attributes(g, node_states, name = 'state_y')
                nx.set_node_attributes(g, interval, name = 'time_y')
                obs = g.copy()
            elif obs_type == 'torch':
                nx.set_node_attributes(g, interval, name = 'time_y')
                obs = from_networkx(g.copy(), group_node_attrs=['state_x','time_x','time_y'], group_edge_attrs=['weight'])
                state = np.array(list(node_states.values()))
                obs.y = torch.tensor(state)


            #append the snapshot to sim result
            simulation_result.append(obs)
        return simulation_result

    raise Exception("Acceptable values for obs_storage are: 'numpy', 'networkx', 'torch' ")

def forward(distance,
            num_results=10,
            obs_type = 'numpy',
            graph_kind = 'connSW',
            graph_size=1000,
            graph_beta = None,
            inf_beta = None,
            inf_gamma = None,
            inf_initial_frac = None,
            interval_lower = -1,
            ):

    if isinstance(distance,int):
        distance = [distance]

    #generate results
    results = []
    for n in range(num_results):
        (g,inf_model, sir_config) = setup(graph_kind, graph_size, graph_beta, inf_beta, inf_gamma, inf_initial_frac)
        iterations = run_sim(distance, interval_lower, g, inf_model)

        intervals =[len(iterations) -max(distance)-1]
        for d in distance:
            intervals.append(intervals[0] + d)

        simulation_result = format_sim_result(intervals, iterations, obs_type, g.copy())

        #append two results that are distance apart
        results.append({'observations': simulation_result,
                        'base_graph': g,
                        'SIR_config': sir_config})


    return results

def backward(distance,
            num_results=10,
            obs_type = 'numpy',
            graph_kind = 'connSW',
            graph_size=1000,
            graph_beta = None,
            inf_beta = None,
            inf_gamma = None,
            inf_initial_frac = None,
            interval_lower = -1,
            ):

    if isinstance(distance,int):
        distance = [distance]

    #generate results
    results = []
    for n in range(num_results):
        (g,inf_model, sir_config) = setup(graph_kind, graph_size, graph_beta, inf_beta, inf_gamma, inf_initial_frac)
        iterations = run_sim(distance, interval_lower, g, inf_model)

        intervals =[len(iterations)-1]
        for d in distance:
            intervals.append(intervals[0] - d)

        simulation_result = format_sim_result(intervals, iterations, obs_type, g.copy())

        #append observations, the starting graph, the starting SIR model
        results.append({'observations': simulation_result,
                        'base_graph': g,
                        'SIR_config': sir_config})

    return results


def graph_eval(obs_true, obs_pred, display=False):
    from sklearn.metrics import classification_report, ConfusionMatrixDisplay
    import matplotlib.pyplot as plt

    if not isinstance(obs_true, np.ndarray) or not isinstance(obs_pred, np.ndarray):
        raise Exception('Observation inputs must be numpy arrays')


    cr = classification_report(obs_true, obs_pred, zero_division=0)

    if display:
        ConfusionMatrixDisplay.from_predictions(obs_true, obs_pred)
        plt.show()
        print(cr)

    return cr

