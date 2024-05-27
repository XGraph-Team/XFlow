import pandas as pd
import networkx as nx
import requests
from io import StringIO

# Download FAF data
faf_url = "https://www.bts.gov/sites/bts.dot.gov/files/2021-06/faf_commodity_flow_matrix.csv"
response = requests.get(faf_url)
data = StringIO(response.text)
faf_df = pd.read_csv(data)

# Inspect the dataframe
print(faf_df.head())

# Construct the graph
G = nx.DiGraph()

for index, row in faf_df.iterrows():
    origin = row['Origin']
    destination = row['Destination']
    weight = row['Tons']

    # Add edges to the graph
    G.add_edge(origin, destination, weight=weight)

print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
