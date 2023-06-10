import itertools

import networkx as nx
import numpy as np

from ..source_results import MultiSourceResult
from ...utils import estimators
from .. import single_source


def netsleuth(I, G, hypotheses_per_step=1):
    """Implements the multi-source NETSLEUTH algorithm to score combinations
    of nodes in G.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    G : NetworkX Graph
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.
    hypotheses_per_step : int (default 1)
        number of candidate sources to be kept per iteration of NETSLEUTH.
        Particular usage is described in greater detail in `Notes` section.

    Notes
    -----
    The number of source hypotheses returned will be hypotheses_per_step*[number of seed nodes],
    the latter of which is automatically determined via minimum description length
    calculations.

    NETSLEUTH is described in [1]_ and [2]_.

    NETSLEUTH has linear complexity with the number of edges of the infected subgraph,
    edges of the frontier set, and vertices of the infected subgraph.

    The standard n-source version of NETSLEUTH operates as follows:

    1. Obtain Source 1 via single-source method

    2. Delete Source 1 from infection subgraph; obtain Source 2 via single-source method

        ...

    n. Delete Source n-1 from infection subgraph; obtain Source n via single-source method.

    This does not lend itself to ranking alternative hypotheses, so we implement a
    more general variant:

    1. Obtain top ``hypotheses_per_step``-many candidates for Source 1 via single-source
    method; each corresponds to one hypothesis source set, each of size 1

    2. For each hypothesis source set, delete these nodes from a copy of the infection subgraph,
    then obtain top ``hypotheses_per_step``-many candidates for Source 2 via single-source
    method; construct ``|source sets| * hypotheses_per_step`` new source sets to replace the old
    source sets, each of size 2

        ...

    n. For each hypothesis source set, delete these nodes from a copy of the infection subgraph,
    then obtain top ``hypotheses_per_step``-many candidates for Source n via single-source
    method; construct |source sets|*``hypotheses_per_step`` new source sets to replace the old
    source sets, each of size n


    Examples
    --------
    >>> result = cosasi.multiple_source.netsleuth(I, G, number_sources=3, hypotheses_per_step=3)

    References
    ----------
    .. [1] B. Prakash, J. Vreeken, C. Faloutsos,
        "Spotting Culprits in Epidemics: How Many and Which Ones?"
        IEEE 12th International Conference on Data Mining, 2012
        https://ieeexplore.ieee.org/document/6413787
    .. [2] L. Ying and K. Zhu,
        "Diffusion Source Localization in Large Networks"
        Synthesis Lectures on Communication Networks, 2018
    """
    multisource_scores = {}
    mdl_decreasing = True
    this_mdl = np.inf
    last_mdl = np.inf
    i = 1

    while mdl_decreasing:
        if i == 1:
            step_result = single_source.netsleuth(I, G)
            for s in step_result.topn(hypotheses_per_step):
                multisource_scores[(s)] = estimators.description_length([s], G)
        else:
            new_multisource_scores = {}
            for j in multisource_scores.keys():
                H = I.copy()
                if i == 2:
                    H.remove_nodes_from([j])
                else:
                    H.remove_nodes_from(j)
                step_result = single_source.netsleuth(H, G)
                for s in step_result.topn(hypotheses_per_step):
                    if i == 2:
                        new_s = tuple([j] + [s])
                    else:
                        new_s = tuple(list(j) + [s])
                    new_multisource_scores[new_s] = estimators.description_length(
                        list(new_s), G
                    )
            multisource_scores = new_multisource_scores

        # update mdl tracker
        last_mdl = this_mdl
        this_mdl = min(multisource_scores.values())
        mdl_decreasing = this_mdl < last_mdl
        i += 1

    result = MultiSourceResult(
        source_type="multi-source",
        inference_method="netsleuth",
        scores=multisource_scores,
        G=G,
        reverse=False,
    )
    return result


def fast_multisource_netsleuth(I, G, number_sources=None):
    """Greedily runs single-source NETSLEUTH on each estimated infection subgraph attributable
    to each of the hypothesized number of sources.

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

    Examples
    --------
    >>> result = cosasi.multiple_source.fast_multisource_netsleuth(I, G)

    Notes
    -----
    Unofficial variant of multisource NETSLEUTH intended for fast computation and ranking,
    because the typical multisource version does not lend itself to scoring many possible
    source sets.

    NETSLEUTH is described in [1]_ and [2]_. More authoritative implementation is found in
    `multisource.netsleuth`.

    References
    ----------
    .. [1] B. Prakash, J. Vreeken, C. Faloutsos,
        "Spotting Culprits in Epidemics: How Many and Which Ones?"
        IEEE 12th International Conference on Data Mining, 2012
        https://ieeexplore.ieee.org/document/6413787
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
            for k, v in single_source.netsleuth(subgraphs[i], G).data["scores"].items()
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
        inference_method="fast multi-source netsleuth",
        scores=product_scores,
        G=G,
    )
    return result
