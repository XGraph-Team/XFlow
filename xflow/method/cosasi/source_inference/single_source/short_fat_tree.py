import math
import random

import networkx as nx
import numpy as np

from ...utils import longest_list_len
from ..source_results import SingleSourceResult


def short_fat_tree(I, G, infection_rate=0.1):
    """Implements the Short-Fat-Tree (SFT) algorithm to score all nodes in G.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    G : NetworkX Graph
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.
    infection_rate : float (optional)
        Inter-node infection efficiency from the original contagion process
        must be in [0, 1]

    Examples
    --------
    >>> result = cosasi.single_source.short_fat_tree(I, G)

    Notes
    -----
    Algorithm attempts to find infection center by identifying the vertex with
    largest weighted boundary node degree. The algorithm was introduced in [1]_.

    Nodes outside the infection subgraph receive a score of negative infinity.

    References
    ----------
    .. [1] K. Zhu and L. Ying,
        "Information source detection in the SIR model: A sample-path-based approach."
        IEEE/ACM Transactions on Networking, 2014
        https://ieeexplore.ieee.org/document/6962907
    """
    N = len(I)
    # each node receives its own node ID at time 0
    t_messages = {i: list() for i in I.nodes}  # timestep t
    t_minus_messages = {i: [i] for i in I.nodes}  # timestep t-1
    earlier_messages = {i: set() for i in I.nodes}  # timesteps earlier than t-1
    all_messages = {i: {i} for i in I.nodes}  # full history

    t = 1
    while longest_list_len(all_messages.values()) < N:
        for v in I.nodes:
            new_ids = set(t_minus_messages[v]) - earlier_messages[v]
            if new_ids:  # v received new node IDs in t-1 time slot
                for u in I.neighbors(v):
                    # v broadcasts the new node IDs to its neighbors
                    t_messages[u] += new_ids
        t += 1

        # update message history
        earlier_messages = {
            i: earlier_messages[i].union(t_minus_messages[i]) for i in I.nodes
        }
        all_messages = {
            i: all_messages[i].union(t_minus_messages[i]).union(t_messages[i])
            for i in I.nodes
        }
        # push back recent message record
        t_minus_messages = t_messages
        t_messages = {i: list() for i in I.nodes}

    # S keys are the set of nodes that receive |I| distinct node IDs
    S = {
        v: weighted_boundary_node_degree(I=I, G=G, v=v, infection_rate=infection_rate)
        if v in I.nodes and len(all_messages[v]) >= N
        else -np.inf
        for v in G.nodes
    }
    result = SingleSourceResult(
        source_type="single-source", inference_method="short-fat-tree", scores=S, G=G
    )
    return result


def weighted_boundary_node_degree(I, G, v, infection_rate=0.01, return_boundary=False):
    """Computes the weighted boundary node degree (WBND) with respect to node v and
    the set of infected nodes I.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    G : NetworkX Graph
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.
    infection_rate : float (optional)
        Inter-node infection efficiency from the original contagion process
        must be in [0, 1]
    return_boundary : bool
        if True, you get both the weighted boundary node degree and the involved boundary nodes
        if False, you only get the weighted boundary node degree

    Notes
    -----
    This implementation is based on the WBND Algorithm, described in Algorithm 2.2
    on p. 10 of [1]_.

    References
    ----------
    .. [1] L. Ying and K. Zhu,
        "Diffusion Source Localization in Large Networks"
        Synthesis Lectures on Communication Networks, 2018
    """
    wbnd = 0
    v_infection_eccentricity = nx.eccentricity(I, v=v)
    v_boundary = [
        w
        for w in I.nodes
        if nx.shortest_path_length(G, source=v, target=w) == v_infection_eccentricity
    ]
    v_boundary_len = len(v_boundary)
    wbnd = sum([G.degree(u) - v_boundary_len for u in v_boundary]) * abs(
        math.log(1 - infection_rate)
    )
    if return_boundary:
        return wbnd, v_boundary
    return wbnd
