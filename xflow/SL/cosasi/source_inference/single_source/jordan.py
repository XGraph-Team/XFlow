import networkx as nx
import numpy as np

from ...utils import soft_eccentricity
from ..source_results import SingleSourceResult


def jordan_centrality(I, G):
    """Computes the infection eccentricity of each node in the infection subgraph. To
    produce a score with highest value corresponding to the Jordan center, we return
    the inverse of the infection eccentricity.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    G : NetworkX Graph
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.

    Notes
    -----
    The Jordan infection center is the vertex with minimum infection eccentricity.
    This is described in [1]_ and [2]_.

    Nodes outside the infection subgraph receive a score of negative infinity.


    Examples
    --------
    >>> result = cosasi.single_source.jordan_centrality(I, G)

    References
    ----------
    .. [1] L. Ying and K. Zhu,
        "On the Universality of Jordan Centers for Estimating Infection Sources in Tree Networks"
        IEEE Transactions of Information Theory, 2017
    .. [2] L. Ying and K. Zhu,
        "Diffusion Source Localization in Large Networks"
        Synthesis Lectures on Communication Networks, 2018
    """
    scores = {
        v: 1 / soft_eccentricity(I, v=v) if v in I.nodes else -np.inf for v in G.nodes
    }
    result = SingleSourceResult(
        source_type="single-source",
        inference_method="jordan centrality",
        scores=scores,
        G=G,
        reverse=True,
    )
    return result
