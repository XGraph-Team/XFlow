import networkx as nx
import numpy as np
import torch_geometric.datasets as ds
import random
import ndlib
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
import torch_geometric

from torch_geometric.datasets import Planetoid, EmailEUCore, MyketDataset, BitcoinOTC, HydroNet, GDELTLite, ICEWS18, PolBlogs
from torch_geometric.utils import to_networkx

print(torch_geometric.__version__)

def convert_to_graph(dataset):
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)
    return G

def convert_temporal_to_graph(dataset):
    G = nx.DiGraph()  # Directed graph since temporal data often implies direction
    data = dataset[0]
    
    # Assuming 'src', 'dst', 'ts' are attributes in the temporal data
    edges = zip(data.src.numpy(), data.dst.numpy())
    G.add_edges_from(edges)
    
    return G

def convert_temporal_to_graph_attr(data):
    G = nx.DiGraph()  # Directed graph since temporal data often implies direction
    
    # Check available attributes and construct edges accordingly
    if hasattr(data, 'src') and hasattr(data, 'dst'):
        edges = zip(data.src.numpy(), data.dst.numpy())
    elif hasattr(data, 'edge_index') and data.edge_index is not None:
        edges = zip(data.edge_index[0].numpy(), data.edge_index[1].numpy())
    else:
        raise AttributeError("The dataset does not have expected edge attributes.")

    G.add_edges_from(edges)
    
    return G

def add_edge_weights(G, min_weight, max_weight):
    config = mc.Configuration()
    for a, b in G.edges():
        weight = random.uniform(min_weight, max_weight)
        weight = round(weight, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        G[a][b]['weight'] = weight
    return G, config
    
def CiteSeer():
    dataset = Planetoid(root='./Planetoid', name='CiteSeer')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def PubMed():
    dataset = Planetoid(root='./Planetoid', name='PubMed')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def Cora():
    dataset = Planetoid(root='./Planetoid', name='Cora')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def photo():
    dataset = ds.Amazon(root='./geo', name = 'Photo')
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)
    g = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(5,20)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def coms():
    dataset = ds.Amazon(root='./geo', name = 'Computers')
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)
    g = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(5,20)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def email_eu_core():
    dataset = EmailEUCore(root='./EmailEUCore')
    G = convert_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def reddit():
    dataset = ds.JODIEDataset(root='./JODIE', name='Reddit')
    G = convert_temporal_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def last_fm():
    dataset = ds.JODIEDataset(root='./JODIE', name='LastFM')
    G = convert_temporal_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def bitcoin_otc():
    dataset = BitcoinOTC(root='./BitcoinOTC')
    data = dataset[0]
    if data.edge_index is None:
        raise ValueError("The edge_index is None for BitcoinOTC dataset")
    G = convert_temporal_to_graph_attr(data)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def polblogs():
    dataset = PolBlogs(root='./PolBlogs')
    data = dataset[0]
    G = convert_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

def myket():
    dataset = MyketDataset(root='./Myket')
    G = convert_temporal_to_graph(dataset)
    G = nx.convert_node_labels_to_integers(G, first_label=0)
    G, config = add_edge_weights(G, 0.1, 0.5)
    return G, config

# def main():
#     # Generate and configure graphs for different datasets
#     g_citeseer, config_citeseer = CiteSeer()
#     g_pubmed, config_pubmed = PubMed()
#     g_cora, config_cora = Cora()
#     g_photo, config_photo = photo()
#     g_coms, config_coms = coms()
#     g_bitcoin_otc, config_bitcoin_otc = bitcoin_otc()
#     g_email_eu_core, config_email_eu_core = email_eu_core()
#     g_polblogs, config_polblogs = polblogs()
#     g_reddit, config_reddit = reddit()
#     g_last_fm, config_last_fm = last_fm()
#     g_myket, config_myket = myket()

#     # Print the number of nodes and edges in each graph as a simple verification
#     print("CiteSeer: Nodes = {}, Edges = {}".format(len(g_citeseer.nodes()), len(g_citeseer.edges())))
#     print("PubMed: Nodes = {}, Edges = {}".format(len(g_pubmed.nodes()), len(g_pubmed.edges())))
#     print("Cora: Nodes = {}, Edges = {}".format(len(g_cora.nodes()), len(g_cora.edges())))
#     print("Photo: Nodes = {}, Edges = {}".format(len(g_photo.nodes()), len(g_photo.edges())))
#     print("Computers: Nodes = {}, Edges = {}".format(len(g_coms.nodes()), len(g_coms.edges())))
#     print("Bitcoin OTC: Nodes = {}, Edges = {}".format(len(g_bitcoin_otc.nodes()), len(g_bitcoin_otc.edges())))
#     print("Email EU Core: Nodes = {}, Edges = {}".format(len(g_email_eu_core.nodes()), len(g_email_eu_core.edges())))
#     print("PolBlogs: Nodes = {}, Edges = {}".format(len(g_polblogs.nodes()), len(g_polblogs.edges())))
#     print("Reddit: Nodes = {}, Edges = {}".format(len(g_reddit.nodes()), len(g_reddit.edges())))
#     print("LastFM: Nodes = {}, Edges = {}".format(len(g_last_fm.nodes()), len(g_last_fm.edges())))
#     print("Myket: Nodes = {}, Edges = {}".format(len(g_myket.nodes()), len(g_myket.edges())))

# if __name__ == "__main__":
#     main()
