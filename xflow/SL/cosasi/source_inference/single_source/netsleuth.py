import networkx as nx
import numpy as np
import warnings

from ..source_results import SingleSourceResult


def netsleuth(I, G):
    """Implements the single-source NETSLEUTH algorithm to score all nodes in G.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    G : NetworkX Graph
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.

    Notes
    -----
    NETSLEUTH is described in [1]_. General idea is that, under mean field
    approximation, the probability of observing an infection subgraph given a
    particular source s is proportional to the sth entry of the largest eigenvector
    of the infection subgraph Laplacian. The implementation below is described in
    [2]_.

    Nodes outside the infection subgraph (i.e. the frontier set) receive a score of
    negative infinity.

    NETSLEUTH has linear complexity with the number of edges of the infected subgraph,
    edges of the frontier set, and vertices of the infected subgraph.


    Examples
    --------
    >>> result = cosasi.single_source.netsleuth(I, G)

    References
    ----------
    .. [1] B. A. Prakash, J. Vreeken, C. Faloutsos,
        "Efficiently spotting the starting points of an epidemic in a large graph"
        Knowledge and Information Systems, 2013
        https://link.springer.com/article/10.1007/s10115-013-0671-5
    .. [2] L. Ying and K. Zhu,
        "Diffusion Source Localization in Large Networks"
        Synthesis Lectures on Communication Networks, 2018
    """
    warnings.filterwarnings("ignore", module="networkx\..*")

    L = nx.laplacian_matrix(G).toarray()
    infection_indices = [i for i in I.nodes]
    L_I = L[np.ix_(infection_indices, infection_indices)]
    eigenvalues, eigenvectors = np.linalg.eig(L_I)
    largest_eigenvalue = max(eigenvalues)
    largest_eigenvector = eigenvectors[:, list(eigenvalues).index(largest_eigenvalue)]
    scores = {
        v: largest_eigenvector[infection_indices.index(v)]
        if v in infection_indices
        else -np.inf
        for v in G.nodes
    }
    result = SingleSourceResult(
        source_type="single-source", inference_method="netsleuth", scores=scores, G=G
    )
    return result
