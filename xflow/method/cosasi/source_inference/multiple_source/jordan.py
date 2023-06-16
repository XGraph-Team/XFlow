import itertools

import networkx as nx
import numpy as np

from ..source_results import MultiSourceResult
from ...utils import estimators
from .. import single_source


def fast_multisource_jordan_centrality(I, G, number_sources=None):
    """Greedily runs single-source Jordan centrality on each estimated infection
    subgraph attributable to each of the hypothesized number of sources.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    G : NetworkX Graph
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.
    number_sources : int or None (optional)
        if int, this is the hypothesized number of infection sources
        if None, estimates the number of sources

    Notes
    -----
    The Jordan infection center is the vertex with minimum infection eccentricity.
    This is described in [1]_ and [2]_.

    Examples
    --------
    >>> result = cosasi.multiple_source.fast_multisource_jordan_centrality(I, G)

    References
    ----------
    .. [1] L. Ying and K. Zhu,
        "On the Universality of Jordan Centers for Estimating Infection Sources in Tree Networks"
        IEEE Transactions of Information Theory, 2017
    .. [2] L. Ying and K. Zhu,
        "Diffusion Source Localization in Large Networks"
        Synthesis Lectures on Communication Networks, 2018
    """
    if not number_sources:
        number_sources, subgraphs = estimators.number_sources(
            I, return_source_subgraphs=True
        )
    else:
        number_sources, subgraphs = estimators.number_sources(
            I, number_sources=number_sources, return_source_subgraphs=True
        )

    sources_scores = [
        {
            k: v
            for k, v in single_source.jordan_centrality(subgraphs[i], G)
            .data["scores"]
            .items()
            if v != -np.inf
        }
        for i in range(number_sources)
    ]
    data = [list(d.keys()) for d in sources_scores]
    product_scores = {}

    for item in itertools.product(*data):
        idx = tuple(item)
        product_scores[idx] = 0
        for i in range(len(idx)):
            product_scores[idx] += sources_scores[i][idx[i]]
    result = MultiSourceResult(
        source_type="multi-source",
        inference_method="fast multi-source jordan centrality",
        scores=product_scores,
        G=G,
    )
    return result
