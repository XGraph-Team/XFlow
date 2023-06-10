import networkx as nx
import torch_geometric.datasets as ds
import ndlib.models.ModelConfig as mc
import numpy as np
import random

from torch_geometric.datasets import Planetoid

def CiteSeer():
    dataset = Planetoid(root='./Planetoid', name='CiteSeer')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    g = nx.convert_node_labels_to_integers(g, first_label=0, ordering='default', label_attribute=None)

    return g

def PubMed():
    dataset = Planetoid(root='./Planetoid', name='PubMed')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    g = nx.convert_node_labels_to_integers(g, first_label=0, ordering='default', label_attribute=None)

    return g

def Cora():
    dataset = Planetoid(root='./Planetoid', name='Cora')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    g = nx.convert_node_labels_to_integers(g, first_label=0, ordering='default', label_attribute=None)

    return g

def photo():

    dataset = ds.Amazon(root='./geo', name = 'Photo')
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)
    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    g = nx.convert_node_labels_to_integers(g, first_label=0, ordering='default', label_attribute=None)

    return g

def coms():

    dataset = ds.Amazon(root='./geo', name = 'Computers')
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)
    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    g = nx.convert_node_labels_to_integers(g, first_label=0, ordering='default', label_attribute=None)

    return g

def connSW(n, k, p):
    # n The number of nodes
    # k Each node is joined with its k nearest neighbors in a ring topology.
    # p The probability of rewiring each edge

    g = nx.connected_watts_strogatz_graph(n, k, p)
    while nx.is_connected(g) == False:
        g = nx.connected_watts_strogatz_graph(n,k, p)    

    return g

def rand(n, p, seed):
    # n The number of nodes
    # p Probability for edge creation
    # seed Seed for random number generator (default=None)
    random.seed(seed)
    np.random.seed(seed)
    g = nx.fast_gnp_random_graph(n, p, seed=seed)

    return g
