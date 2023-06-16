import math
import random

import networkx as nx

from ...utils import list_product
from ..source_results import SingleSourceResult


def rumor_centrality_root(I, v, return_all_values=True):
    """Computes rumor centrality for all nodes, assuming a spanning tree rooted at v.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    v : graph index - str, int, etc.
        The vertex rooting
    return_all_values : bool
        Specifies whether you want the full rumor centrality dict.
        If False, returns only the value for node v

    Notes
    -----
    Rumor centrality was introduced in the seminal work [1]_. This is a more "literal"
    interpretation of their algorithm. `rumor_centrality` averages these results over all
    possible BFS rooting schemes.

    References
    ----------
    .. [1] S. Devavrat and T. Zaman,
        "Rumors in a network: Who's the culprit?."
        IEEE Transactions on Informatidon Theory, 2011
        https://devavrat.mit.edu/wp-content/uploads/2017/10/Rumors-in-a-network-whos-the-culprit.pdf
    """
    N = len(I)
    G = nx.bfs_tree(I, v)

    # sort nodes by depth from leaves to root
    depths = nx.shortest_path_length(G, v)
    nodes_by_depth = sorted(depths, key=depths.get, reverse=True)

    # message-passing data objects; indexing is dict[destination][source]
    t = {
        i: {j: 0 for j in nodes_by_depth} for i in nodes_by_depth
    }  # subtree size messages
    p = {
        i: {j: 0 for j in nodes_by_depth} for i in nodes_by_depth
    }  # subtree product messages
    r = {i: 0 for i in nodes_by_depth}  # rumor centrality values

    for u in nodes_by_depth:
        children_u = [e[1] for e in G.out_edges(u)]
        if u != v:
            parent_u = list(G.in_edges(u))[0][0]
        if G.out_degree(u) == 0:
            # u is a leaf
            if "parent_u" in locals():
                t[parent_u][u] = 1
                p[parent_u][u] = 1
        else:
            if u != v:
                # u is not root
                if "parent_u" in locals():
                    t[parent_u][u] = 1 + sum([t[u][j] for j in children_u])
                    p[parent_u][u] = t[parent_u][u] * list_product(
                        [p[u][j] for j in children_u]
                    )
    for u in nodes_by_depth[::-1]:
        children_u = [e[1] for e in G.out_edges(u)]
        if u == v:
            # u is root
            r[u] = math.factorial(N) / list_product([p[u][j] for j in children_u])
        else:
            parent_u = list(G.in_edges(u))[0][0]
            r[u] = r[parent_u] * t[parent_u][u] / (N - t[parent_u][u])
    for u in nodes_by_depth:
        r[u] /= len(G)
    if not return_all_values:
        return r[v]
    return r


def rumor_centrality(I, G=None, v=None, normalize=True, only_roots=False):
    """Computes rumor centrality for all nodes in G.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    G : NetworkX Graph (optional)
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.
        This is not actually used, but exists to match the format of other algorithms
    v : graph index - str, int, etc. (optional)
        if provided, returns the rumor centrality of v only.
    normalize : bool
        If True, scales all rumor centrality values to between 0 and 1
    only_roots : bool
        Aggregation strategy, as we compute rumor_centrality_root over all possible
        root nodes.
        If True, we only keep the rumor_centrality_root value for the root node
        If False, we keep the rumor_centrality_root values for all nodes

    Notes
    -----
    Rumor centrality was introduced in the seminal work [1]_. `rumor_centrality_root` is a
    more "literal" interpretation of their algorithm. `rumor_centrality` (this function)
    averages these results over all possible BFS rooting schemes.


    Examples
    --------
    >>> result = cosasi.single_source.rumor_centrality(I, G)

    References
    ----------
    .. [1] S., Devavrat and T. Zaman,
        "Rumors in a network: Who's the culprit?."
        IEEE Transactions on Information Theory, 2011
        https://devavrat.mit.edu/wp-content/uploads/2017/10/Rumors-in-a-network-whos-the-culprit.pdf
    """
    if v and v not in I:
        raise ValueError("Provided node is not in I.")

    # iterate over possible roots, and average over spanning trees
    rumor_centrality_dict = {i: 0 for i in I.nodes}
    for root in rumor_centrality_dict:
        if only_roots:
            rumor_centrality_dict[root] = rumor_centrality_root(
                I, root, return_all_values=False
            )
        else:
            r = rumor_centrality_root(I, root, return_all_values=True)
            for node in I.nodes:
                if node in r:
                    rumor_centrality_dict[node] += r[node]
    for node in rumor_centrality_dict:
        rumor_centrality_dict[node] /= len(I)
    if normalize:
        max_val = max(rumor_centrality_dict.values())
        for node in rumor_centrality_dict:
            rumor_centrality_dict[node] /= max_val
    if v:
        return rumor_centrality_dict[v]
    result = SingleSourceResult(
        source_type="single-source",
        inference_method="rumor centrality",
        scores=rumor_centrality_dict,
        G=G,
    )
    return result
