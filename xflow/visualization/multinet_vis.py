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
network_layers = [nx.erdos_renyi_graph(20, 1), nx.erdos_renyi_graph(20, 1)]

# Assign random positions for the nodes in each network layer
for G in network_layers:
    for node in G.nodes():
        G.nodes[node]["pos"] = (random.uniform(-1, 1), random.uniform(-1, 1))

# Get some of the nodes in layer 0 and layer 1
nodes_pool_layer0 = int(len(network_layers[0].nodes()) * 1)
nodes_pool_layer1 = int(len(network_layers[1].nodes()) * 1)

# Randomly sample nodes from both layers
nodes_layer0_to_connect = random.sample(network_layers[0].nodes(), nodes_pool_layer0)
nodes_layer1_to_connect = random.sample(network_layers[1].nodes(), nodes_pool_layer1)

# Pair and connect selected nodes
for node0, node1 in zip(nodes_layer0_to_connect, nodes_layer1_to_connect):
    network_layers[0].add_edge(node0, node1)
    network_layers[1].add_edge(node0, node1)

# Initialize the app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css",
        'styles.css'
    ]
)

app.layout = html.Div(
    [
        # Left side of the screen (col-6)
        html.Div([
            # Controls and Status Information section
            html.Div([
                # Row for "Initial infected nodes" and DataTable
                html.Div([

                    # Column for Initial infected nodes
                    html.Div([
                        
                        # Label for Initial infected nodes
                        html.Div([
                            html.Label("Initial infected nodes:", style={"font-weight": "bold"}),
                        ], className="col-12"),  # This div ensures the label takes up the full width of its parent column
                        
                        # Input for Initial infected nodes
                        html.Div([
                            dcc.Input(id="input-infected", type="number", value=1)
                        ], className="col-12"),  # This div ensures the input takes up the full width of its parent column

                    ], className="col-6"),  # This column takes up half of the left-hand side

                    # DataTable column with padding to the right
                    html.Div([
                        dash_table.DataTable(id="status-table"),
                    ], className="col-6", style={"padding-right": "100px"}),  # This column also takes up half of the left-hand side and has padding to the right

                ], className="row"), 

                # Beta (Infection rate) label and slider
                html.Div([
                    html.Label("Beta (Infection rate):", style={"font-weight": "bold"}),
                    dcc.Slider(id="beta-slider", min=0, max=1, step=0.1, value=0.8)
                ], className="col-12"),  # This div will ensure its content starts on a new line

                # Gamma (Recovery rate) label and slider
                html.Div([
                    html.Label("Gamma (Recovery rate):", style={"font-weight": "bold"}),
                    dcc.Slider(id="gamma-slider", min=0, max=1, step=0.1, value=0.01)
                ], className="col-12"),

                # Time Step label and slider
                html.Div([
                    html.Label("Time Step:", style={"font-weight": "bold"}),
                    dcc.Slider(
                        id="time-slider",
                        min=0,
                        max=TIME_STEPS - 1,
                        value=0,
                        marks={str(i): f"{i}" for i in range(TIME_STEPS)},
                        step=None,
                    )
                ], className="col-12"),
            ], style={"height": "400px", "width": "100%", "padding-top": "20px"}),

            # Energy Plot section
            html.Div([
                dcc.Graph(id="energy-plot", style={"height": "550px", "width": "100%"})
            ], className="col-12"),
        ], className="col-4"),

        # Right side of the screen (col-6)
        html.Div([
            # 3D Scatter Plot section
            html.Div([
                dcc.Graph(id="3d-scatter-plot", style={"height": "1200px", "width": "100%"})
            ], className="col-12"),
    
        ], className="col-8"),
    ],
    className="row"
)

# for both table and graph
@app.callback(
    Output("status-table", "data"),
    Output("status-table", "columns"),
    Output("3d-scatter-plot", "figure"),
    Output("energy-plot", "figure"),
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

    # Create a DataFrame and format it for use with DataTable
    df = pd.DataFrame([status_counts_total])
    data = df.to_dict("records")
    columns = [{"name": i, "id": i} for i in df.columns]

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

    layer2_results = []

    for iteration in range(len(model_results_self[0])):  # Assuming both lists have the same length
        layer2_energy_self_count = 0
        layer2_energy_diff_count = 0
        
        # Check self energy for nodes in layer 0
        for node in nodes_layer0_to_connect:
            if model_results_self[0][iteration]["updated_status"].get(node) == 1:
                layer2_energy_self_count += 1
                
        # Check self energy for nodes in layer 1
        for node in nodes_layer1_to_connect:
            if model_results_self[1][iteration]["updated_status"].get(node) == 1:
                layer2_energy_self_count += 1

        # Check diff energy between pairs of nodes
        for node0, node1 in zip(nodes_layer0_to_connect, nodes_layer1_to_connect):
            status_node0 = model_results_self[0][iteration]["updated_status"].get(node0)
            status_node1 = model_results_self[1][iteration]["updated_status"].get(node1)
            
            # Check the cases
            if (status_node0 == 1 and status_node1 in [0, 2]) or (status_node1 == 1 and status_node0 in [0, 2]):
                layer2_energy_diff_count += 1

        # Store the results
        layer2_results.append({
            'iteration': iteration,
            'layer2_energy_self_count': layer2_energy_self_count,
            'layer2_energy_diff_count': layer2_energy_diff_count
        })

    print('layer2_results', layer2_results)

    graph_data = []

    # Create traces for edges and nodes
    for idx, network in enumerate(network_layers):
        
        edge_color = "pink" if idx == 0 else "lightblue" if idx == 1 else "#888"  # Default color is #888
        
        edge_trace = go.Scatter3d(
            x=[],
            y=[],
            z=[],
            line={"width": 0.5, "color": edge_color},
            hoverinfo="none",
            mode="lines",
            name="Edges"  # Assign a name for the edges trace
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
            name="Nodes"  # Assign a name for the nodes trace
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
            if node in model_results_self[idx][time_step]["updated_status"]:
                status = model_results_self[idx][time_step]["updated_status"][node]
            color = (
                "red" if status == 1 else "green" if status == 2 else "grey"
            )  # Color based on the infection status
            node_trace["marker"]["color"] += (color,)

        graph_data.extend((edge_trace, node_trace))

    # Add inter-layer edges to trace
    inter_edge_trace = go.Scatter3d(
        x=[],
        y=[],
        z=[],
        line={"width": 0.5, "color": "#888"},
        hoverinfo="none",
        mode="lines",
        name="Inter-Layer-Edges"
    )

    # Add inter-layer edges to trace
    for node0, node1 in zip(network_layers[0].nodes(), network_layers[1].nodes()):
        x0, y0 = network_layers[0].nodes[node0]["pos"]
        x1, y1 = network_layers[1].nodes[node1]["pos"]
        inter_edge_trace["x"] += (x0, x1, None)
        inter_edge_trace["y"] += (y0, y1, None)
        inter_edge_trace["z"] += (0, 1, None)

    graph_data.append(inter_edge_trace)

    # Define layout
    layout = go.Layout(
        scene=dict(
            xaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False, zeroline=False, showline=False, showbackground=False, showgrid=False),
            yaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False, zeroline=False, showline=False, showbackground=False, showgrid=False),
            zaxis=dict(title="", showticklabels=False, range=[-1, 1], autorange=False, zeroline=False, showline=False, showbackground=False, showgrid=False),
            aspectratio=dict(x=1, y=1, z=1),
            camera=dict(eye=dict(x=1.2, y=1.2, z=1.2)),
        ),
        legend=dict(
            x=0.5,
            y=1.1,
            xanchor='center',
            yanchor='middle',
            orientation='h',
            font=dict(
                size=20
            )
        )
    )

    figure = {"data": graph_data, "layout": layout}

    # Extracting the data
    iterations = [entry['iteration'] for entry in model_results_self[0]]
    y_values_0 = [entry['energy_diff_count'] + entry['energy_self_count'] for entry in model_results_self[0]]
    y_values_1 = [entry['energy_diff_count'] + entry['energy_self_count'] for entry in model_results_self[1]]
    y_values_2 = [entry['layer2_energy_self_count'] + entry['layer2_energy_diff_count'] for entry in layer2_results]

    # Plotting the data
    energy = go.Figure()

    # blue
    energy.add_trace(go.Scatter(x=iterations, y=y_values_0, mode='lines', name='Lower Layer', fill='tozeroy', fillcolor='rgba(173, 216, 230, 0.3)'))
    # red
    energy.add_trace(go.Scatter(x=iterations, y=y_values_1, mode='lines', name='Upper Layer', fill='tozeroy', fillcolor='rgba(255, 182, 193, 0.3)'))
    # green
    energy.add_trace(go.Scatter(x=iterations, y=y_values_2, mode='lines', name='Inter-Layer', fill='tozeroy', fillcolor='rgba(144, 238, 144, 0.3)'))

    energy.update_layout(title='Energy vs. Time Step',
                        xaxis_title='Time Step',
                        yaxis_title='Energy',
                        title_x=0.5)  # This centers the title
        
    energy.update_layout(
        legend=dict(
            x=0.5,   # this centers the legend horizontally
            y=1.1,   # this positions the legend just above the chart
            xanchor='center',  # this is to ensure the 'x' value refers to the center of the legend
            orientation='h'    # this ensures the legend items are arranged horizontally
        )
    )

    return data, columns, figure, energy

def run_simulations(network_layers, num_infected, beta, gamma, TIME_STEPS):
    models = [get_sir_model(layer, num_infected, beta, gamma) for layer in network_layers]
    return [run_sir_model(model, TIME_STEPS) for model in models]

if __name__ == "__main__":
    app.run_server(debug=True)