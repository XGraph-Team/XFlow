import math

import networkx as nx
import numpy as np
import scipy as sp

from ..source_results import SingleSourceResult


def lisn(I, G, t=None, infection_rate=0.1):
    """Implements the algorithm from Localizing the Information Source in a Network to
    score all nodes in G [1]_.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    G : NetworkX Graph
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.
    t : int (optional)
        the observation timestep corresponding to I
    infection_rate : float (optional)
        Inter-node infection efficiency from the original contagion process
        must be in [0, 1]

    Notes
    -----
    Because the probabilities can be quite small, we report the log-score, rather than the
    raw score itself.

    To our knowledge, this algorithm has no official name; it is referred to as "Algorithm 1"
    in its corresponding publication [1]_. We dub it LISN, the acronym of the publication
    title (Localizing the Information Source in a Network).

    Nodes outside the infection subgraph receive a score of negative infinity.


    Examples
    --------
    >>> result = cosasi.single_source.lisn(I, G)

    References
    ----------
    .. [1] G. Nie and C. Quinn,
        "Localizing the Information Source in a Network"
        TrueFact 2019: KDD 2019 Workshop on Truth Discovery and Fact Checking: Theory and Practice, 2019
    """
    scores = {v: -np.inf for v in G.nodes}
    for v in I.nodes:
        scores[v] = 0
        for u in G.nodes:
            if u == v:
                continue
            n = nx.shortest_path_length(G, v, u)
            if u in I.nodes:
                scores[v] += math.log(distance_prob(t, n, infection_rate))
            else:
                scores[v] += math.log(1 - distance_prob(t, n, infection_rate))
    result = SingleSourceResult(
        source_type="single-source", inference_method="lisn", scores=scores, G=G
    )
    return result


def distance_prob(t, n, infection_rate=0.1):
    """Approximates the probability of one node receiving the rumor/contagion from another node
    n edges away within time t.

    Parameters
    ----------
    t : int (optional)
        the observation timestep corresponding to I
        This is not actually used, but exists to match the format of other algorithms
    n : int
        shortest path distance
    infection_rate : float (optional)
        Inter-node infection efficiency from the original contagion process
        must be in [0, 1]

    Notes
    -----
    This function is defined in Section 3 of [1]_.

    References
    ----------
    .. [1] G. Nie and C. Quinn,
        "Localizing the Information Source in a Network"
        TrueFact 2019: KDD 2019 Workshop on Truth Discovery and Fact Checking: Theory and Practice, 2019

    """

    def gamma(s, x):
        def gamma_integrand(x, s):
            return x ** (s - 1) * math.e ** (-x)

        return sp.integrate.quad(gamma_integrand, 0, x, args=s)[0]

    return gamma(n, infection_rate * t) / sp.special.gamma(n)
