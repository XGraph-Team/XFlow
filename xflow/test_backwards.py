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

# example code using backward function
# generate a dataset of 5 backward flow simulations with observations saved as numpy lists at time intervals 1 and 4
output = backward(distance=[1, 4], 
                  interval_lower=0, 
                  obs_type='numpy', 
                  num_results=5,
                  graph_size=graph_size, 
                  graph_beta=graph_beta, 
                  inf_beta=infection_beta, 
                  inf_gamma=infection_gamma)

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

    # example code to use graph_eval
    start_time = observations[0]['time']  # first observation time
    start_obs = observations[0]['observation']  # first observation

    # for observations other than the starting observation, ask the model to predict the observation at that time interval
    for obs in observations[1:]:
        interval = obs['time']  # time interval to predict

        # make prediction... as an example, we will use the original starting observation as the predicted observation for all intervals
        pred_obs = start_obs
        true_obs = obs['observation']

        # evaluate accuracy of this observation
        eval_dict = graph_eval(true_obs, pred_obs)

        #print the evaluation metrics
        print('Prediction for time interval', interval, '- ', end='')
        for key, value in eval_dict.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    print(f'{key}_{sub_key}: {round(sub_value, 3)}, ', end='')
            else:
                print(f'{key}: {round(value, 3)}, ', end='')
        print()
    print()

############################################################################################################

# example code using backward function
# generate a dataset of 5 backward flow simulations with observations saved as torch data objects at time intervals 1 and 4
output = backward(distance=[1, 4], 
                  interval_lower=0, 
                  obs_type='torch', 
                  num_results=5,
                  graph_size=graph_size, 
                  graph_beta=graph_beta, 
                  inf_beta=infection_beta, 
                  inf_gamma=infection_gamma)

# Display general information about these simulation results
print('Observations are of type:', type(output[0]['observations'][0]), end='\n\n')

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

    # Print observation time intervals for this result
    print('Observations at time intervals: ', sep='', end='')
    for ss in observations:
        print(f'{ss.time_y}, ', end='')  # Access the time attribute directly from the data object
    print('\n')

    # example code to use graph_eval
    start_time = observations[0].time_y  # first observation time
    start_obs = observations[0].y.numpy()  # first observation

    # for observations other than the starting observation, ask the model to predict the observation at that time interval
    for obs in observations[1:]:
        interval = obs.time_y.item()  # time interval to predict

        # make prediction... as an example, we will use the original starting observation as the predicted observation for all intervals
        pred_obs = start_obs
        true_obs = obs.y.numpy()

        # evaluate accuracy of this observation
        eval_dict = graph_eval(true_obs, pred_obs)

        # print the evaluation metrics
        print('Prediction for time interval', interval, '- ', end='')
        for key, value in eval_dict.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    print(f'{key}_{sub_key}: {round(sub_value, 3)}, ', end='')
            else:
                print(f'{key}: {round(value, 3)}, ', end='')
        print()
    print()

############################################################################################################
# Example code using backward function
# Generate a dataset of 5 backward flow simulations with observations saved as networkx graphs at time intervals 1 and 4
output = backward(distance=[1, 4], 
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

    # example code to use graph_eval
    start_time = observations[0].graph['time_y']  # first observation time
    start_obs = np.array(list(nx.get_node_attributes(observations[0], 'state_y').values()))  # first observation

    # for observations other than the starting observation, ask the model to predict the observation at that time interval
    for obs in observations[1:]:
        interval = obs.graph['time_y']  # time interval to predict

        # make prediction... as an example, we will use the original starting observation as the predicted observation for all intervals
        pred_obs = start_obs
        true_obs = np.array(list(nx.get_node_attributes(obs, 'state_y').values()))

        # evaluate accuracy of this observation
        eval_dict = graph_eval(true_obs, pred_obs)

        # print the evaluation metrics
        print('Prediction for time interval', interval, '- ', end='')
        for key, value in eval_dict.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    print(f'{key}_{sub_key}: {round(sub_value, 3)}, ', end='')
            else:
                print(f'{key}: {round(value, 3)}, ', end='')
        print()
    print()