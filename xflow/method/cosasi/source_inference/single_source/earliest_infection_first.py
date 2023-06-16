import random

import networkx as nx
import numpy as np

from ...utils import soft_eccentricity
from ..source_results import SingleSourceResult


def earliest_infection_first(I, G, observer_dict):
    """Implements the Earliest Infection First algorithm to score all nodes in I.

    This algorithm is useful if some infection timestamp information is available.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    G : NetworkX Graph
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.
    observer_dict : dict
        observers dictionary, a la contagion.get_observers()

    Notes
    -----
    This is the greedy algorithm outlined in Section 3 of [1]_. We iterate over rooting
    schemes and score each source hypothesis by the cost of their corresponding EIF
    spreading tree. In particular, we implement the "cost-based ranking" approach described
    in Section 4 of [1]_.

    References
    ----------
    .. [1] K. Zhu, Z. Chen, L. Ying,
        "Locating Contagion Sources in Networks with Partial Timestamps"
        Data Mining and Knowledge Discovery, 2016
        https://link.springer.com/article/10.1007/s10618-015-0435-9
    """
    if not nx.is_connected(G):
        raise ValueError("G must be connected for EIF algorithm.")
    observers = observer_dict.copy()
    # SI-ify the observers dict
    for k in observers:
        if isinstance(observers[k], list):
            observers[k] = observers[k][0]
    mu = _estimate_mu(G, observers)
    alpha = [i[0] for i in sorted(observers.items(), key=lambda j: j[1]) if i[0] in I]
    scores = {i: np.inf for i in G}
    for v in I:
        scores[v] = eif_root(
            root=v,
            I=I,
            G=G,
            observers=observers,
            mu=mu,
            alpha=alpha,
            only_return_cost=True,
        )
    result = SingleSourceResult(
        source_type="single-source",
        inference_method="earliest infection first",
        scores=scores,
        G=G,
        reverse=False,
    )
    return result


def eif_root(root, I, G, observers, mu, alpha, only_return_cost=True):
    """Computes the cost of a greedy EIF spreading tree whose "patient zero" is root.

    Parameters
    ----------
    root : graph index - str, int, etc.
        The vertex rooting
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    G : NetworkX Graph
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.
    observers : dict
        observers dictionary, a la contagion.get_observers()
    mu : float
        a constant, estimated by _estimate_mu()
    alpha : list
        list of vertices in observers dictionary, sorted from earliest to latest timestamp-wise
    only_return_cost : bool
        if True, only returns the calculated spreading tree's cost

    Notes
    -----
    This is the greedy algorithm outlined in Section 3 of [1]_.

    References
    ----------
    .. [1] K. Zhu, Z. Chen, L. Ying,
        "Locating Contagion Sources in Networks with Partial Timestamps"
        Data Mining and Knowledge Discovery, 2016
        https://link.springer.com/article/10.1007/s10618-015-0435-9
    """
    timestamps = observers.copy()
    if root not in timestamps:
        timestamps[root] = min(timestamps.values()) - mu
    spreading_tree = nx.Graph()
    spreading_tree.add_nodes_from([root])
    spreading_tree_cost = 0
    for a in alpha:
        path = None
        path_cost = np.inf
        for m in spreading_tree:
            # find a modified shortest path (msp) from m to a
            surrogate = G.copy()
            to_remove = [v for v in alpha if v != a] + [
                v for v in spreading_tree if v != m
            ]
            surrogate.remove_nodes_from(to_remove)
            try:
                msp = nx.shortest_path(surrogate, source=m, target=a)
            except:
                # no msp exists
                continue
            # calculate msp's cost
            msp_len = len(msp)
            msp_cost = msp_len * (
                (((timestamps[a] - timestamps[m]) / msp_len) - mu) ** 2
            )
            # compare cost to existing minimum path cost
            if msp_cost < path_cost:
                path = msp
                path_cost = msp_cost
        if isinstance(path, type(None)):
            continue
        # add path to spreading tree
        for i in range(len(path) - 1):
            spreading_tree.add_edge(path[i], path[i + 1])
        # update observers/timestamps
        path_len_iter = 1
        path_factor = (timestamps[path[-1]] - timestamps[path[0]]) / len(path)
        for g in path:
            timestamps[g] = timestamps[path[0]] + (path_len_iter - 1) * path_factor
            path_len_iter += 1
        # update tree cost
        spreading_tree_cost += path_cost
    # add remaining nodes
    not_in_tree = [v for v in G if v not in spreading_tree]
    new_len = len(not_in_tree)
    while new_len > 0:
        for v in not_in_tree:
            breaker = False
            for p in G.neighbors(v):
                if breaker:
                    break
                if p in spreading_tree:
                    spreading_tree.add_edge(v, p)
                    timestamps[v] = (
                        timestamps[p] + mu
                    )  # cost does not change in this step
                    breaker = True
        old_len = new_len
        not_in_tree = [v for v in G if v not in spreading_tree]
        new_len = len(not_in_tree)
        if new_len == old_len:
            break
    if only_return_cost:
        return spreading_tree_cost
    return spreading_tree, spreading_tree_cost, timestamps


def _estimate_mu(G, observers):
    """Estimates the constant mu from the quadratic tree cost function.

    Parameters
    ----------
    G : NetworkX Graph
        The network for the diffusion process to run on
    observers : dict
        observers dictionary, a la contagion.get_observers()

    Notes
    -----
    The mu parameter is introduced in Equation 2 of [1]_.

    Some very minor details are modified for extensibility throughout cosasi.
    For instance, the observers record is a dictionary of time steps, rather than
    a list of time stamps. Non-observers are recorded with an infection time of infinity
    rather than "*", as described in the paper [1]_.

    References
    ----------
    .. [1] K. Zhu, Z. Chen, L. Ying,
        "Locating Contagion Sources in Networks with Partial Timestamps"
        Data Mining and Knowledge Discovery, 2016
        https://link.springer.com/article/10.1007/s10618-015-0435-9
    """
    num_val = 0
    denom_val = 0
    for v in observers:
        for w in observers:
            if v != w and v != np.inf and w != np.inf:
                num_val += abs(observers[v] - observers[w])
                denom_val += nx.shortest_path_length(G, source=v, target=w)
    return num_val / denom_val
