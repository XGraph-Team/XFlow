import networkx as nx
import plotly.graph_objects as go
import random
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# todo
# Step 1: Randomly draw a 50-node graph using NetworkX
G = nx.gnm_random_graph(50, 100)

# Step 2: Create an initial plot using Plotly
pos = nx.spring_layout(G)
node_trace = go.Scatter(
    x=[pos[node][0] for node in G.nodes()],
    y=[pos[node][1] for node in G.nodes()],
    mode="markers",
    marker=dict(
        size=20,
        color="blue",
    ),
)
edge_trace = go.Scatter(
    x=[],
    y=[],
    mode="lines",
    line=dict(width=0.5, color="#888"),
)
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_trace["x"] += tuple([x0, x1, None])
    edge_trace["y"] += tuple([y0, y1, None])

fig = go.Figure(data=[edge_trace, node_trace],
               layout=go.Layout(
                   showlegend=False,
                   hovermode="closest",
                   margin=dict(b=20, l=5, r=5, t=40),
                   annotations=[
                       dict(
                           text="Red Node Ratio:",
                           showarrow=False,
                           xref="paper",
                           yref="paper",
                           x=0,
                           y=-0.1
                       )
                   ],
                   xaxis=dict(
                       showline=False,
                       zeroline=False,
                   ),
                   yaxis=dict(
                       showline=False,
                       zeroline=False,
                   ),
                   height=600,
                   autosize=True,  # Set autosize to True
               ))

# Step 3: Create the Dash app
app = dash.Dash(__name__)

# Step 4: Define the app layout
app.layout = html.Div([
    dcc.Graph(figure=fig, id="graph"),
    html.Div([
        html.Label("Red Node Ratio:"),
        dcc.Slider(
            id="ratio-slider",
            min=0,
            max=1,
            step=0.1,
            value=0.5,
            marks={i/10: str(i/10) for i in range(11)},
        )
    ])
])

# Step 5: Define the callback function for slider changes
@app.callback(
    Output("graph", "figure"),
    [Input("ratio-slider", "value")]
)
def update_red_nodes(ratio):
    num_red_nodes = int(ratio * len(G.nodes))
    red_nodes = random.sample(G.nodes, num_red_nodes)

    fig.data[1].marker.color = ["red" if node in red_nodes else "blue" for node in G.nodes]
    return fig

# Step 6: Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
