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
TIME_STEPS = 5
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


# Create two random graphs
network_layers = [nx.erdos_renyi_graph(100, 0.06), nx.erdos_renyi_graph(100, 0.06)]

# Assign random positions for the nodes in each network layer
for G in network_layers:
    for node in G.nodes():
        G.nodes[node]["pos"] = (random.uniform(-1, 1), random.uniform(-1, 1))

# Initialize the app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css"
    ],
)

# Initialize the app layout
app.layout = html.Div(
    [
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
            marks={str(i): f"Time {i}" for i in range(TIME_STEPS)},
            step=None,
        ),
        dash_table.DataTable(id="status-table"),
        dcc.Graph(id="3d-scatter-plot", style={"height": "800px", "width": "800px"}),
    ]
)


@app.callback(
    Output("status-table", "data"),
    Output("status-table", "columns"),
    [
        Input("time-slider", "value"),
        Input("input-infected", "value"),
        Input("beta-slider", "value"),
        Input("gamma-slider", "value"),
    ],
)
def update_table(time_step, num_infected, beta, gamma):
    models = [
        get_sir_model(layer, num_infected, beta, gamma) for layer in network_layers
    ]
    model_results = [run_sir_model(model, TIME_STEPS) for model in models]

    # Compute the counts of each status at the current time step
    status_counts = {"Susceptible": 0, "Infected": 0, "Recovered": 0}
    for result in model_results:
        for status, count in result[time_step]["node_count"].items():
            if status == 0:
                status_counts["Susceptible"] += count
            elif status == 1:
                status_counts["Infected"] += count
            elif status == 2:
                status_counts["Recovered"] += count

    # Create a DataFrame and format it for use with DataTable
    df = pd.DataFrame([status_counts])
    data = df.to_dict("records")
    columns = [{"name": i, "id": i} for i in df.columns]

    return data, columns


@app.callback(
    Output("3d-scatter-plot", "figure"),
    [
        Input("time-slider", "value"),
        Input("input-infected", "value"),
        Input("beta-slider", "value"),
        Input("gamma-slider", "value"),
    ],
)
def update_graph(time_step, num_infected, beta, gamma):
    models = [
        get_sir_model(layer, num_infected, beta, gamma) for layer in network_layers
    ]
    model_results = [run_sir_model(model, TIME_STEPS) for model in models]

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
                "red" if status == 1 else "green" if status == 2 else "blue"
            )  # Color based on the infection status
            node_trace["marker"]["color"] += (color,)

        data.extend((edge_trace, node_trace))

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
