import networkx as nx
import ndlib.models.ModelConfig as mc
import ndlib.models.epidemics as ep
from time import time
from graph_generation import Cora, CiteSeer, PubMed, connSW, ER, coms, photo
import matplotlib.pyplot as plt

# 
size = 50
beta = 0.1
gamma = 0.01
G, config = connSW(size, beta)

# Model selection
model = ep.SIRModel(G)

# Model Configuration
config = mc.Configuration()
config.add_model_parameter('beta', beta)  # The infection rate
config.add_model_parameter('gamma', gamma)  # The recovery rate
config.add_model_parameter("fraction_infected", 0.1)  # Initial fraction of infected nodes

model.set_initial_status(config)

# Simulation execution for 10 steps
iterations = model.iteration_bunch(10)
print(iterations)

# Update the graph with the status from the last iteration
for i, node_status in model.status.items():
    G.nodes[i]['status'] = node_status

# After the simulation, set up the colors for the nodes
status_colors = {0: 'green',  # Susceptible
                 1: 'red',    # Infected
                 2: 'blue'}   # Recovered
colors = [status_colors[node[1]['status']] for node in G.nodes(data=True)]

# Draw the graph and save to a file
pos = nx.spring_layout(G)  # Compute layout for visualizing the graph
nx.draw(G, pos, node_color=colors, with_labels=False, node_size=20)

# Save the plot as a file
plt.savefig('graph_infected_state.png', format='PNG')

# Close the plot to release memory
plt.close()
