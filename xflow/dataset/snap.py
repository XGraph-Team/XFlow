import networkx as nx
import requests
import random
import ndlib.models.ModelConfig as mc

def download_snap_dataset(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def add_edge_weights(G, min_weight, max_weight):
    config = mc.Configuration()
    for a, b in G.edges():
        weight = random.uniform(min_weight, max_weight)
        weight = round(weight, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        G[a][b]['weight'] = weight
    return G, config

def load_snap_graph(filename):
    G = nx.read_edgelist(filename)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def main():
    # Example with the Facebook social circles dataset
    url = "https://snap.stanford.edu/data/facebook_combined.txt.gz"
    filename = "facebook_combined.txt.gz"
    download_snap_dataset(url, filename)
    g_facebook, config_facebook = load_snap_graph(filename)
    print("Facebook: Nodes = {}, Edges = {}".format(len(g_facebook.nodes()), len(g_facebook.edges())))

if __name__ == "__main__":
    main()
