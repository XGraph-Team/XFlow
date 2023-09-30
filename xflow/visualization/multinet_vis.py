# imports
import dash
import random
from dash import dcc
from dash import html

from dash.dependencies import Input, Output
import plotly.graph_objs as go
import networkx as nx
import ndlib.models.epidemics as ep
from ndlib.models.ModelConfig import Configuration

import pandas as pd
from dash import dash_table

# - - - - - - - - - - - - - - - - - - - - -
# Set the number of simulation time steps
TIME_STEPS = 10
# - - - - - - - - - - - - - - - - - - - - -

def get_sir_model(graph, num_infected, beta, gamma):
    """Returns a configured SIR model for the given graph."""
    model = ep.SIRModel(graph)
    config = Configuration()
    config.add_model_parameter("beta", beta)
    config.add_model_parameter("gamma", gamma)
    infected_nodes = random.sample(list(graph.nodes()), num_infected)
    config.add_model_initial_configuration("Infected", infected_nodes)
    model.set_initial_status(config)
    return model

def run_sir_model(model, time_steps):
    """Runs the given SIR model for the given number of time steps."""
    return model.iteration_bunch(time_steps)

# Create two random graphs with different numbers of nodes
network_layers = [nx.erdos_renyi_graph(10, 1), nx.erdos_renyi_graph(10, 1)]

# Assign random positions for the nodes in each network layer
for G in network_layers:
    for node in G.nodes():
        G.nodes[node]["pos"] = (random.uniform(-1, 1), random.uniform(-1, 1))

# Get some of the nodes in layer 0
num_nodes_to_connect = int(len(network_layers[0].nodes()) * 0.1)
nodes_layer0_to_connect = random.sample(network_layers[0].nodes(), num_nodes_to_connect)

# Pair each selected node in layer 0 with a node in layer 1
for node0, node1 in zip(nodes_layer0_to_connect, network_layers[1].nodes()):
    network_layers[0].add_edge(node0, node1)
    network_layers[1].add_edge(node0, node1)

# Initialize the app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css"
    ],
)

app.layout = html.Div(
    [
        # html.Div([
        #     dcc.Graph(id="energy-plot", style={"height": "400px", "width": "100%"})
        # ], className="col-9"), 

        html.Div([
            dcc.Graph(id="3d-scatter-plot", style={"height": "800px", "width": "100%"}),
        ], className="col-9"),  # This div wraps the scatter plot

        html.Div([
            html.Label("Initial infected nodes:", style={"font-weight": "bold"}),
            html.P("The initial number of infected nodes in the graph."),
            dcc.Input(id="input-infected", type="number", value=1),
            html.Label("Beta (Infection rate):", style={"font-weight": "bold"}),
            html.P(
                "The probability of disease transmission from an infected node to a susceptible node."
            ),
            dcc.Slider(id="beta-slider", min=0, max=1, step=0.1, value=0.8),
            html.Label("Gamma (Recovery rate):", style={"font-weight": "bold"}),
            html.P(
                "The probability of an infected node moving into the recovered stage in each time step."
            ),
            dcc.Slider(id="gamma-slider", min=0, max=1, step=0.1, value=0.01),
            html.Label("Time:", style={"font-weight": "bold"}),
            html.P("The time step at which to view the state of the graph."),
            dcc.Slider(
                id="time-slider",
                min=0,
                max=TIME_STEPS - 1,
                value=0,
                marks={str(i): f"{i}" for i in range(TIME_STEPS)},
                step=None,
            ),
            dash_table.DataTable(id="status-table"),
        ], className="col-3"),  # This div wraps the controls
    ],
    className="row"  # Bootstrap's row class to contain both of the above divs
)

# for both table and graph
@app.callback(
    Output("status-table", "data"),
    Output("status-table", "columns"),
    Output("3d-scatter-plot", "figure"),
    [
        Input("time-slider", "value"),
        Input("input-infected", "value"),
        Input("beta-slider", "value"),
        Input("gamma-slider", "value"),
    ],
)
def update_table_graph(time_step, num_infected, beta, gamma):
    # Part 1
    for layer in network_layers:
        print("layer", layer)

    model_results = run_simulations(network_layers, num_infected, beta, gamma, TIME_STEPS)
    model_results_modified = model_results

    if len(model_results) > 1:
        # Extract the status of each node in layer 0 and layer 1 at the current time step
        layer0_results = model_results[0]
        layer1_results = model_results[1]

        print("Status of each node in Layer 0:")
        for result in layer0_results:
            if 'status' in result:
                for node_id, status in result['status'].items():
                    print(f"Node {node_id}: Status {status}")

        print("\nStatus of each node in Layer 1:")
        for result in layer1_results:
            if 'status' in result:
                for node_id, status in result['status'].items():
                    print(f"Node {node_id}: Status {status}")

    # # Initialize status count dictionaries for each layer
    status_counts_total = {"Susceptible": 0, "Infected": 0, "Recovered": 0}
    status_counts_layer0 = {"Susceptible": 0, "Infected": 0, "Recovered": 0}
    status_counts_layer1 = {"Susceptible": 0, "Infected": 0, "Recovered": 0}

    # Compute the counts of each status at the current time step for each layer
    for layer_index, result in enumerate(model_results):
        for status, count in result[time_step]["node_count"].items():
            if status == 0:
                status_counts_total["Susceptible"] += count
                # print("layer_index", layer_index)
                if layer_index == 0:
                    status_counts_layer0["Susceptible"] += count
                elif layer_index == 1:
                    status_counts_layer1["Susceptible"] += count
            elif status == 1:
                status_counts_total["Infected"] += count
                if layer_index == 0:
                    status_counts_layer0["Infected"] += count
                elif layer_index == 1:
                    status_counts_layer1["Infected"] += count
            elif status == 2:
                status_counts_total["Recovered"] += count
                if layer_index == 0:
                    status_counts_layer0["Recovered"] += count
                elif layer_index == 1:
                    status_counts_layer1["Recovered"] += count


    # print('model_results', model_results)
    # for layer_index, result in enumerate(model_results):
    #     print('layer_index', layer_index)
    #     print('result', result)
    #     for status, count in result[time_step]["node_count"].items():
    #         print('status', status)

    #     # Iterating over the list of result dictionaries
    # for layer_index, result_dict in enumerate(model_results):
    #     print('layer_index', layer_index)
        
    #     # Iterating over the dictionaries in the result list
    #     for single_result in result_dict:
    #         # Extracting the 'iteration' value
    #         iteration = single_result.get('iteration')
    #         print('iteration', iteration)
            
    #         # Extracting the 'status' value
    #         status = single_result.get('status')
    #         print('status', status)


    # Create a DataFrame and format it for use with DataTable
    df = pd.DataFrame([status_counts_total])
    data = df.to_dict("records")
    columns = [{"name": i, "id": i} for i in df.columns]

    print("Step", time_step)
    # print("Susceptible", status_counts["Susceptible"])
    # print("Infected", status_counts["Infected"])
    # print("Recovered", status_counts["Recovered"])

    print("Susceptible status_counts_total", status_counts_total["Susceptible"])
    print("Infected status_counts_total", status_counts_total["Infected"])
    print("Recovered status_counts_total", status_counts_total["Recovered"])

    print("Susceptible status_counts_layer0", status_counts_layer0["Susceptible"])
    print("Infected status_counts_layer0", status_counts_layer0["Infected"])
    print("Recovered status_counts_layer0", status_counts_layer0["Recovered"])

    print("Susceptible status_counts_layer1", status_counts_layer1["Susceptible"])
    print("Infected status_counts_layer1", status_counts_layer1["Infected"])
    print("Recovered status_counts_layer1", status_counts_layer1["Recovered"])

    # Calculate the energy for layer 0
    high_energy_layer0 = status_counts_layer0["Infected"]
    print ("high_energy_layer0", high_energy_layer0)

    low_energy_layer0 = status_counts_layer0["Susceptible"] + status_counts_layer0["Recovered"]
    print ("low_energy_layer0", low_energy_layer0)
   
    # Calculate the energy for layer 1
    high_energy_layer1 = status_counts_layer1["Infected"]
    print ("high_energy_layer1", high_energy_layer1)

    low_energy_layer1 = status_counts_layer1["Susceptible"] + status_counts_layer1["Recovered"]
    print ("low_energy_layer1", low_energy_layer1)

    # Assuming network_layers is a list of NetworkX graph objects
    for layer_index, graph in enumerate(network_layers):
        print(f"Layer {layer_index}:")
        
        for node in graph.nodes():
            status = graph.nodes[node].get('status')  # Replace 'status' with the actual attribute name if it's different
            num_neighbors = len(list(graph.neighbors(node)))
            
            print(f"Node {node}: Status {status}, Number of Neighbors {num_neighbors}")

    # Assuming network_layers is a list of NetworkX graph objects
    for layer_index, graph in enumerate(network_layers):
        print(f"Layer {layer_index}:")
        
        # Initialize the counter for nodes with different status from their neighbors
        different_status_counter = 0
        
        for node in graph.nodes():
            status = graph.nodes[node].get('status')  # Replace 'status' with the actual attribute name if it's different
            num_neighbors = len(list(graph.neighbors(node)))
            
            print(f"Node {node}: Status {status}, Number of Neighbors {num_neighbors}")
            
            # Iterate through the neighbors of the current node
            for neighbor in graph.neighbors(node):
                neighbor_status = graph.nodes[neighbor].get('status')
                
                # Check if the status of the node and its neighbor are not the same
                if status != neighbor_status:
                    different_status_counter += 1
        
        # Print the count of nodes with different status from their neighbors in this layer
        print(f"Number of nodes in Layer {layer_index} with different status from their neighbors: {different_status_counter}")

    # Part 2
    for result in model_results_modified:
        # Initialize an empty dictionary for 'updated_status' 
        # to hold status values across iterations
        updated_status = {}
        for iteration in result:
            if iteration['iteration'] == 0:
                # For the first iteration, 'updated_status' is same as 'status'
                iteration['updated_status'] = iteration['status'].copy()
            else:
                # For subsequent iterations, update 'updated_status' based on the 'status'
                for key, value in iteration['status'].items():
                    updated_status[key] = value
                iteration['updated_status'] = updated_status.copy()

            # Update our ongoing 'updated_status' with the current 'updated_status'
            updated_status = iteration['updated_status'].copy()
    print('model_results_modified', model_results_modified)

    model_results_diff = model_results_modified
    for result in model_results_diff:
        for iteration in result:
            updated_status = iteration['updated_status']
            
            energy_diff_count = 0
            keys = list(updated_status.keys())
            
            for i in range(len(keys)):
                for j in range(i+1, len(keys)):
                    val_i = updated_status[keys[i]]
                    val_j = updated_status[keys[j]]
                    
                    # If val_i or val_j is 2, consider it as 0
                    if val_i == 2:
                        val_i = 0
                    if val_j == 2:
                        val_j = 0
                    
                    # Check if they're different
                    if val_i != val_j:
                        energy_diff_count += 1
            
            iteration['energy_diff_count'] = energy_diff_count

    print('model_results_diff', model_results_diff)

    model_results_self = model_results_diff
    for result in model_results_self:
        for iteration in result:
            updated_status = iteration['updated_status']
            
            energy_self_count = sum([1 for value in updated_status.values() if value == 1])
            
            iteration['energy_self_count'] = energy_self_count
    print('model_results_self', model_results_self)

    graph_data = []
    # Create traces for edges and nodes
    for idx, network in enumerate(network_layers):
    
        edge_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            line={"width": 0.5, "color": "#888"},
            hoverinfo="none",
            mode="lines",
        )

        node_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            mode="markers",
            hoverinfo="text",
            marker={
                "showscale": False,
                "colorscale": "Viridis",
                "reversescale": True,
                "color": [],
                "size": 6,
                "opacity": 0.8,
                "line": {"width": 0.5, "color": "#888"},
            },
        )

        # Add edges to trace
        for edge in network.edges():
            x0, y0 = network.nodes[edge[0]]["pos"]
            x1, y1 = network.nodes[edge[1]]["pos"]
            edge_trace["x"] += (x0, x1, None)
            edge_trace["y"] += (y0, y1, None)
            edge_trace["z"] += (idx, idx, None)

        # Add nodes to trace
        for node in network.nodes:
            x, y = network.nodes[node]["pos"]
            node_trace["x"] += (x,)
            node_trace["y"] += (y,)
            node_trace["z"] += (idx,)
            status = 0
            if node in model_results_modified[idx][time_step]["updated_status"]:
                status = model_results_modified[idx][time_step]["updated_status"][node]
            color = (
                "red" if status == 1 else "green" if status == 2 else "grey"
            )  # Color based on the infection status
            node_trace["marker"]["color"] += (color,)

        graph_data.extend((edge_trace, node_trace))


    # Define layout
    layout = go.Layout(
        scene=dict(
            xaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False),
            yaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False),
            zaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False),
            aspectratio=dict(x=1, y=1, z=1),
            camera=dict(eye=dict(x=1.2, y=1.2, z=1.2)),
        )
    )

    figure = {"data": graph_data, "layout": layout}
    return data, columns, figure

# #backup
# @app.callback(
#     Output("status-table", "data"),
#     Output("status-table", "columns"),
#     [
#         Input("time-slider", "value"),
#         Input("input-infected", "value"),
#         Input("beta-slider", "value"),
#         Input("gamma-slider", "value"),
#     ],
# )
# def update_table(time_step, num_infected, beta, gamma):
#     print('Running update_table')
#     for layer in network_layers:
#         print("layer", layer)

#     # models = [
#     #     get_sir_model(layer, num_infected, beta, gamma) for layer in network_layers
#     # ]
#     # model_results = [run_sir_model(model, TIME_STEPS) for model in models]
#     # print("model_results", model_results)

#     model_results = run_simulations(network_layers, num_infected, beta, gamma, TIME_STEPS)


#     if len(model_results) > 1:
#         # Extract the status of each node in layer 0 and layer 1 at the current time step
#         layer0_results = model_results[0]
#         layer1_results = model_results[1]

#         print("Status of each node in Layer 0:")
#         for result in layer0_results:
#             if 'status' in result:
#                 for node_id, status in result['status'].items():
#                     print(f"Node {node_id}: Status {status}")

#         print("\nStatus of each node in Layer 1:")
#         for result in layer1_results:
#             if 'status' in result:
#                 for node_id, status in result['status'].items():
#                     print(f"Node {node_id}: Status {status}")

#     # # Initialize status count dictionaries for each layer
#     status_counts_total = {"Susceptible": 0, "Infected": 0, "Recovered": 0}
#     status_counts_layer0 = {"Susceptible": 0, "Infected": 0, "Recovered": 0}
#     status_counts_layer1 = {"Susceptible": 0, "Infected": 0, "Recovered": 0}

#     # Compute the counts of each status at the current time step for each layer
#     for layer_index, result in enumerate(model_results):
#         for status, count in result[time_step]["node_count"].items():
#             if status == 0:
#                 status_counts_total["Susceptible"] += count
#                 # print("layer_index", layer_index)
#                 if layer_index == 0:
#                     status_counts_layer0["Susceptible"] += count
#                 elif layer_index == 1:
#                     status_counts_layer1["Susceptible"] += count
#             elif status == 1:
#                 status_counts_total["Infected"] += count
#                 if layer_index == 0:
#                     status_counts_layer0["Infected"] += count
#                 elif layer_index == 1:
#                     status_counts_layer1["Infected"] += count
#             elif status == 2:
#                 status_counts_total["Recovered"] += count
#                 if layer_index == 0:
#                     status_counts_layer0["Recovered"] += count
#                 elif layer_index == 1:
#                     status_counts_layer1["Recovered"] += count


#     print('model_results', model_results)
#     for layer_index, result in enumerate(model_results):
#         print('layer_index', layer_index)
#         print('result', result)
#         for status, count in result[time_step]["node_count"].items():
#             print('status', status)

#         # Iterating over the list of result dictionaries
#     for layer_index, result_dict in enumerate(model_results):
#         print('layer_index', layer_index)
        
#         # Iterating over the dictionaries in the result list
#         for single_result in result_dict:
#             # Extracting the 'iteration' value
#             iteration = single_result.get('iteration')
#             print('iteration', iteration)
            
#             # Extracting the 'status' value
#             status = single_result.get('status')
#             print('status', status)


#     # Create a DataFrame and format it for use with DataTable
#     df = pd.DataFrame([status_counts_total])
#     data = df.to_dict("records")
#     columns = [{"name": i, "id": i} for i in df.columns]

#     print("Step", time_step)
#     # print("Susceptible", status_counts["Susceptible"])
#     # print("Infected", status_counts["Infected"])
#     # print("Recovered", status_counts["Recovered"])

#     print("Susceptible status_counts_total", status_counts_total["Susceptible"])
#     print("Infected status_counts_total", status_counts_total["Infected"])
#     print("Recovered status_counts_total", status_counts_total["Recovered"])

#     print("Susceptible status_counts_layer0", status_counts_layer0["Susceptible"])
#     print("Infected status_counts_layer0", status_counts_layer0["Infected"])
#     print("Recovered status_counts_layer0", status_counts_layer0["Recovered"])

#     print("Susceptible status_counts_layer1", status_counts_layer1["Susceptible"])
#     print("Infected status_counts_layer1", status_counts_layer1["Infected"])
#     print("Recovered status_counts_layer1", status_counts_layer1["Recovered"])

#     # Calculate the energy for layer 0
#     high_energy_layer0 = status_counts_layer0["Infected"]
#     print ("high_energy_layer0", high_energy_layer0)

#     low_energy_layer0 = status_counts_layer0["Susceptible"] + status_counts_layer0["Recovered"]
#     print ("low_energy_layer0", low_energy_layer0)
   
#     # Calculate the energy for layer 1
#     high_energy_layer1 = status_counts_layer1["Infected"]
#     print ("high_energy_layer1", high_energy_layer1)

#     low_energy_layer1 = status_counts_layer1["Susceptible"] + status_counts_layer1["Recovered"]
#     print ("low_energy_layer1", low_energy_layer1)

#     # Assuming network_layers is a list of NetworkX graph objects
#     for layer_index, graph in enumerate(network_layers):
#         print(f"Layer {layer_index}:")
        
#         for node in graph.nodes():
#             status = graph.nodes[node].get('status')  # Replace 'status' with the actual attribute name if it's different
#             num_neighbors = len(list(graph.neighbors(node)))
            
#             print(f"Node {node}: Status {status}, Number of Neighbors {num_neighbors}")

#     # Assuming network_layers is a list of NetworkX graph objects
#     for layer_index, graph in enumerate(network_layers):
#         print(f"Layer {layer_index}:")
        
#         # Initialize the counter for nodes with different status from their neighbors
#         different_status_counter = 0
        
#         for node in graph.nodes():
#             status = graph.nodes[node].get('status')  # Replace 'status' with the actual attribute name if it's different
#             num_neighbors = len(list(graph.neighbors(node)))
            
#             print(f"Node {node}: Status {status}, Number of Neighbors {num_neighbors}")
            
#             # Iterate through the neighbors of the current node
#             for neighbor in graph.neighbors(node):
#                 neighbor_status = graph.nodes[neighbor].get('status')
                
#                 # Check if the status of the node and its neighbor are not the same
#                 if status != neighbor_status:
#                     different_status_counter += 1
        
#         # Print the count of nodes with different status from their neighbors in this layer
#         print(f"Number of nodes in Layer {layer_index} with different status from their neighbors: {different_status_counter}")

#     return data, columns

def run_simulations(network_layers, num_infected, beta, gamma, TIME_STEPS):
    models = [get_sir_model(layer, num_infected, beta, gamma) for layer in network_layers]
    return [run_sir_model(model, TIME_STEPS) for model in models]

# # for update_graph
# @app.callback(
#     Output("3d-scatter-plot", "figure"),
#     [
#         Input("time-slider", "value"),
#         Input("input-infected", "value"),
#         Input("beta-slider", "value"),
#         Input("gamma-slider", "value"),
#     ],
# )

# def update_graph(time_step, num_infected, beta, gamma, model_results):
# def update_graph(time_step, num_infected, beta, gamma):
    print('Running update_graph')

    # models = [
    #     get_sir_model(layer, num_infected, beta, gamma) for layer in network_layers
    # ]
    # model_results = [run_sir_model(model, TIME_STEPS) for model in models]

    model_results = run_simulations(network_layers, num_infected, beta, gamma, TIME_STEPS)

    data = []

    # Create traces for edges and nodes
    for idx, network in enumerate(network_layers):
    
        edge_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            line={"width": 0.5, "color": "#888"},
            hoverinfo="none",
            mode="lines",
        )

        node_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            mode="markers",
            hoverinfo="text",
            marker={
                "showscale": False,
                "colorscale": "Viridis",
                "reversescale": True,
                "color": [],
                "size": 6,
                "opacity": 0.8,
                "line": {"width": 0.5, "color": "#888"},
            },
        )

        # Add edges to trace
        for edge in network.edges():
            x0, y0 = network.nodes[edge[0]]["pos"]
            x1, y1 = network.nodes[edge[1]]["pos"]
            edge_trace["x"] += (x0, x1, None)
            edge_trace["y"] += (y0, y1, None)
            edge_trace["z"] += (idx, idx, None)

        # Add nodes to trace
        for node in network.nodes:
            x, y = network.nodes[node]["pos"]
            node_trace["x"] += (x,)
            node_trace["y"] += (y,)
            node_trace["z"] += (idx,)
            status = 0
            if node in model_results[idx][time_step]["status"]:
                status = model_results[idx][time_step]["status"][node]
            color = (
                "red" if status == 1 else "green" if status == 2 else "grey"
            )  # Color based on the infection status
            node_trace["marker"]["color"] += (color,)

        data.extend((edge_trace, node_trace))

    # Add inter-layer edges to trace
    inter_edge_trace = go.Scatter3d(
        x=[],
        y=[],
        z=[],
        line=dict(width=2, color=[]),  # Set color dynamically
        hoverinfo="none",
        mode="lines",
    )

    # Initialize a list to store the color of each link
    inter_edge_colors = []

    # Add inter-layer edges to trace
    for index, (node0, node1) in enumerate(zip(network_layers[0].nodes(), network_layers[1].nodes())):
        x0, y0 = network_layers[0].nodes[node0]["pos"]
        x1, y1 = network_layers[1].nodes[node1]["pos"]
        inter_edge_trace["x"] += (x0, x1, None)
        inter_edge_trace["y"] += (y0, y1, None)
        inter_edge_trace["z"] += (0, 1, None)
        
        # Color the selected link red, and others light yellow
        link_color = "red" if index == 0 else "blue"  # Change index as needed
        inter_edge_colors.append(link_color)

    # Assign the list of colors to the 'color' attribute of 'line' dictionary
    inter_edge_trace["line"]["color"] = inter_edge_colors

    data.append(inter_edge_trace)

    # Define layout
    layout = go.Layout(
        scene=dict(
            xaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False),
            yaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False),
            zaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False),
            aspectratio=dict(x=1, y=1, z=1),
            camera=dict(eye=dict(x=1.2, y=1.2, z=1.2)),
        )
    )

    return {"data": data, "layout": layout}


if __name__ == "__main__":
    app.run_server(debug=True)