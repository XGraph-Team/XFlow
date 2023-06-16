import operator
import functools

import numpy as np
import networkx as nx


def list_product(l):
    """Returns the product the elements of a list.

    Parameters
    ----------
    l : list
        list of elements you want to multiply
    """
    return functools.reduce(operator.mul, l, 1)


def longest_list(l):
    """Returns the longest list in an array-like of lists.

    Parameters
    ----------
    l : list or array-like
        stores the lists of interest
    """
    return max(l, key=len)


def longest_list_len(l):
    """Returns the length of the longest list in an array-like
    of lists.

    Parameters
    ----------
    l : list or array-like
        stores the lists of interest
    """
    return max(map(len, l))


def soft_eccentricity(G, v):
    """A more flexible calculation of vertex eccentricity.

    Parameters
    ----------
    G : NetworkX graph
       A graph
    v : node
       Return value of specified node

    Notes
    -----
    If `G` is connected and has more than one node, this is regular eccentricity. If `G`
    has only one node, returns 1. If `G` is disconnected, returns infinite eccentricity.
    """
    if nx.number_connected_components(G) > 1:
        return np.inf
    if len(G) == 1:
        return 1
    return nx.eccentricity(G, v=v)


def attack_degree(infected, G, v):
    """Calculates the attack degree of node v in G.

    Parameters
    ----------
    infected : array-like
        infected nodes in G at a particular time step
    G : NetworkX graph
       A graph
    v : node
       Return value of specified node

    Notes
    -----
    Attack degree is the number of infected neighbor nodes a node has.
    Attack degree is defined in Section 4.2.2 of [1]_.

    References
    ----------
    .. [1] B. A. Prakash, J. Vreeken, C. Faloutsos,
        "Efficiently spotting the starting points of an epidemic in a large graph"
        Knowledge and Information Systems, 2013
        https://link.springer.com/article/10.1007/s10115-013-0671-5
    """
    infected_neighbors = [i for i in G.neighbors(v) if i in infected]
    return len(infected_neighbors)


def attack_degree_partition(node_set, infected, G):
    """Divides a node_set into disjoint subsets based on their attack degree.

    Parameters
    ----------
    node_set : array-like
        nodes to partition, e.g. a frontier set
    infected : array-like
        infected nodes in G at a particular time step
    G : NetworkX graph
       A graph

    Notes
    -----
    Attack degree and this partitioning method are outlined in Section 4.2.2 of [1]_.

    References
    ----------
    .. [1] B. A. Prakash, J. Vreeken, C. Faloutsos,
        "Efficiently spotting the starting points of an epidemic in a large graph"
        Knowledge and Information Systems, 2013
        https://link.springer.com/article/10.1007/s10115-013-0671-5
    """
    partitions = {}
    for i in node_set:
        d = attack_degree(infected, G, i)
        if d in partitions.keys():
            partitions[d].append(i)
        else:
            partitions[d] = [i]
    return partitions
