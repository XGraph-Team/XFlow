import numpy as np
import random
import networkx as nx
from networkx import Graph
from torch_geometric.data.data import Data
from . import xflow
from xflow.dataset.nx import connSW
from xflow.flow_tasks import forward, backward, graph_eval

# def main():
#     print("Testing local XFlow package")

# if __name__ == "__main__":
#     main()

graph_size = 1000
graph_beta = 0.1
infection_beta = None
infection_gamma = None

############################################################################################################

# example code using forward function
# generate a dataset of 5 forward flow simulations with observations saved as numpy lists at time intervals 0 and 1
output = forward(distance=1, 
                 interval_lower=0, 
                 obs_type='numpy', 
                 num_results=5,
                 graph_size=graph_size, 
                 graph_beta=graph_beta, 
                 inf_beta=infection_beta, 
                 inf_gamma=infection_gamma)

# print("output", output)

# display general information about these simulation results
print('Observations are of type:', type(output[0]['observations'][0]['observation']), end='\n\n')

for result in output:
    observations = result['observations']
    graph = result['base_graph']
    sir_config = result['SIR_config']  # Use SIR_config here

    # Retrieve beta and gamma values from the Configuration object
    beta = sir_config.config["model"]["beta"]
    gamma = sir_config.config["model"]["gamma"]

    # Print SIR values for this result
    print('SIR model has values: ', sep='', end='')
    print(f'beta = {round(beta, 3)}, gamma = {round(gamma, 3)}')

    # print observation time intervals for this result
    print('Observations at time intervals: ', sep='', end='')
    for ss in observations:
        print(f'{ss["time"]}, ', end='')
    print('\n')

############################################################################################################

# example code using forward function
# generate a dataset of 5 forward flow simulations with observations saved as torch data objects at time intervals 0, 1 and 4
output = forward(distance=[1, 4], 
                 interval_lower=0, 
                 obs_type='torch', 
                 num_results=5,
                 graph_size=graph_size, 
                 graph_beta=graph_beta, 
                 inf_beta=infection_beta, 
                 inf_gamma=infection_gamma)

# print("output", output)

# Display general information about these simulation results
print('Observations are of type:', type(output[0]['observations'][0]), end='\n\n')

for result in output:
    observations = result['observations']
    # print("observations", observations)
    graph = result['base_graph']
    sir_config = result['SIR_config']  # Use SIR_config here

    # Retrieve beta and gamma values from the Configuration object
    beta = sir_config.config["model"]["beta"]
    gamma = sir_config.config["model"]["gamma"]

    # Print SIR values for this result
    print('SIR model has values: ', sep='', end='')
    print(f'beta = {round(beta, 3)}, gamma = {round(gamma, 3)}')

    # Print observation time intervals for this result
    print('Observations at time intervals: ', sep='', end='')
    for ss in observations:
        print(f'{ss.time_y}, ', end='')  # Access the time attribute directly from the data object
    print('\n')

############################################################################################################
# Example code using forward function
# Generate a dataset of 5 forward flow simulations with observations saved as networkx graphs at time intervals t, t-1, t-4
output = forward(distance=[1, 4], 
                 interval_lower=0, 
                 obs_type='networkx', 
                 num_results=5,
                 graph_size=graph_size, 
                 graph_beta=graph_beta, 
                 inf_beta=infection_beta, 
                 inf_gamma=infection_gamma)

print('Observations are of type:', type(output[0]['observations'][0]), end='\n\n')

for result in output:
    observations = result['observations']
    graph = result['base_graph']
    sir_config = result['SIR_config']

    # Retrieve beta and gamma values from the Configuration object
    if sir_config:
        beta = sir_config.config["model"]["beta"]
        gamma = sir_config.config["model"]["gamma"]

        # Print SIR values for this result
        print('SIR model has values: ', sep='', end='')
        print(f'beta = {round(beta, 3)}, gamma = {round(gamma, 3)}')

    # Print observation time intervals for this result
    print('Observations at time intervals: ', sep='', end='')
    for ss in observations:
        print(f'{ss.graph["time_y"]}, ', end='')  # Access the time attribute directly from the graph metadata
    print('\n')

# ############################################################################################################
# # example code using backward function
# # generate a dataset of 5 backward flow simulations with observations saved as torch at time intervals t, t-1, t-4
# output = backward(distance = [1,4],
#                 obs_type = 'torch',
#                 num_results=5,
#                 graph_size=graph_size, 
#                 graph_beta=graph_beta, 
#                 inf_beta=infection_beta, 
#                 inf_gamma=infection_gamma)

# # display general information about these simulation results
# print('Observations are of type:', type(output[0]['observations'][0]), end='\n\n')

# for result in output:
#     observations = result['observations']
#     graph = result['base_graph']
#     sir = result['SIR_config']

#     # Retrieve beta and gamma values from the Configuration object
#     beta = sir_config.config["model"]["beta"]
#     gamma = sir_config.config["model"]["gamma"]

#     # Print SIR values for this result
#     print('SIR model has values: ', sep='', end='')
#     print(f'beta = {round(beta, 3)}, gamma = {round(gamma, 3)}')

#     # Print observation time intervals for this result
#     print('Observations at time intervals: ', sep='', end='')
#     for ss in observations:
#         print(f'{ss.time_y}, ', end='')  # Access the time attribute directly from the data object
#     print('\n')

# ############################################################################################################
# # example code using backward function
# # generate a dataset of 5 backward flow simulations with observations saved as networkx graphs at time intervals t, t-1, t-4
# output = backward(distance = [1,4],
#                 obs_type = 'networkx',
#                 num_results=5,
#                 graph_size=graph_size, 
#                 graph_beta=graph_beta, 
#                 inf_beta=infection_beta, 
#                 inf_gamma=infection_gamma)

# # display general information about these simulation results
# print('Observations are of type:', type(output[0]['observations'][0]), end='\n\n')

# for result in output:
#     observations = result['observations']
#     graph = result['base_graph']
#     sir = result['SIR_config']

#     # Retrieve beta and gamma values from the Configuration object
#     beta = sir_config.config["model"]["beta"]
#     gamma = sir_config.config["model"]["gamma"]

#     # Print SIR values for this result
#     print('SIR model has values: ', sep='', end='')
#     print(f'beta = {round(beta, 3)}, gamma = {round(gamma, 3)}')

#     # Print observation time intervals for this result
#     print('Observations at time intervals: ', sep='', end='')
#     for ss in observations:
#         if isinstance(ss, nx.Graph):
#             times = nx.get_node_attributes(ss, 'time_y')
#             unique_times = set(times.values())
#             for t in unique_times:
#                 print(f'{t}, ', end='')
#         else:
#             print(f'{ss.time_y}, ', end='')  # Access the time attribute directly from the data object
#     print('\n')