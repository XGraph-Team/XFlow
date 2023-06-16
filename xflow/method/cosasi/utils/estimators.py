import math
import random
import warnings

import scipy
import numpy as np
import networkx as nx
from sklearn.cluster import SpectralClustering

from .helpers import attack_degree, attack_degree_partition
from ..source_inference.multiple_source import netsleuth


def source_subgraphs(I, number_sources=2):
    """Subdivides the provided graph into specified number of subgraphs
    via spectral clustering.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    number_sources : int
        The hypothesized number of infection sources
    """
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)

    I_node_list = list(I.nodes)
    A = nx.adjacency_matrix(I)
    subgraphs = []
    sc = SpectralClustering(number_sources, affinity="precomputed", n_init=100)
    sc.fit(scipy.sparse.csr_matrix(A))
    subgraph_labels = sc.labels_
    unique_subgraph_labels = set(subgraph_labels)
    for i in unique_subgraph_labels:
        subgraph_nodes = [I_node_list[j] for j in np.where(subgraph_labels == i)[0]]
        subgraphs.append(I.subgraph(subgraph_nodes))
    return subgraphs


def number_sources(
    I,
    number_sources=None,
    return_source_subgraphs=True,
    number_sources_method="eigengap",
    G=None,
):
    """Manages source subgraph estimation, mostly via spectral analysis and clustering.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    number_sources : int or None (optional)
        if int, this is the hypothesized number of infection sources
        if None, estimates the number of sources via Eigengap heuristic
    return_source_subgraphs : bool
        if True, returns subgraphs of I corresponding to each hypothesized infection source
        if False, does not return subgraphs of I corresponding to each hypothesized infection source
    number_sources_method : str
        method for estimating the number of sources. one of the following options:
        - "eigengap" : uses the Eigengap of the normalized graph Laplacian to estimate the number of clusters
        - "netsleuth" : runs the multi-source NETSLEUTH algorithm and reports the number of seeds
        - "chatter" : invokes a spectral method based on the Chatter algorithm
        if number_sources != None, this doesn't do anything
    G : NetworkX Graph (optional)
        the original network the contagion process was run on
        generally optional (e.g. not needed for eigengap), occassionally required (e.g. needed for netsleuth)

    Notes
    -----
    If the diffusion process is brief or observation is early, and infection sources
    are sufficiently sparse, then the infected subgraphs corresponding to each infection
    source may be the connected components of the input graph. This is described in
    Section 2.6 of [1]_.

    We estimate the number of infection sources by the minimum of the number of connected
    components and the Eigengap heuristic of the provided graph. The Eigengap heuristic
    is described in [2]_.

    With a hypothesized number of infection sources in hand, we partition the graph via
    spectral clustering to provide a list of subgraphs corresponding to each infection
    source [3]_.

    References
    ----------
    .. [1] L. Ying and K. Zhu,
        "Diffusion Source Localization in Large Networks"
        Synthesis Lectures on Communication Networks, 2018
    .. [2] U. von Luxburg,
        "A Tutorial on Spectral Clustering"
        Statistics and Computing, 2007
        https://link.springer.com/article/10.1007/s11222-007-9033-z
    .. [3] A. Damle and V. Minden and L. Ying
        "Simple, direct and efficient multi-way spectral clustering"
        Information and Inference: A Journal of the IMA, 2019
        https://academic.oup.com/imaiai/article/8/1/181/5045955
    """
    if isinstance(number_sources, int):
        if return_source_subgraphs:
            return number_sources, source_subgraphs(I, number_sources=number_sources)
        else:
            return number_sources
    elif isinstance(number_sources, type(None)):
        if number_sources_method.lower() == "eigengap":
            m = eigengap(I)
        elif number_sources_method.lower() == "netsleuth":
            if isinstance(G, type(None)):
                raise ValueError("Need `G` for NETSLEUTH method.")
            netsleuth_result = netsleuth(I=I, G=G, hypotheses_per_step=1)
            m = len(netsleuth_result.topn(1)[0])
        elif number_sources_method.lower() == "chatter":
            if isinstance(G, type(None)):
                raise ValueError("Need `G` for chatter method.")
            m = chatter(I, G)
        else:
            raise NotImplementedError

        if m <= nx.number_connected_components(I):
            subgraphs = [I.subgraph(c) for c in nx.connected_components(I)]
            m = len(subgraphs)
        else:
            subgraphs = source_subgraphs(I, number_sources=m)

        if return_source_subgraphs:
            return m, subgraphs
        else:
            return m
    else:
        raise ValueError("number_sources not recognized: must be an integer or None.")


def chatter(I, G):
    """Estimates the number of sources of a graph diffusion process via the Chatter algorithm.

    Parameters
    ----------
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    G : NetworkX Graph
        The graph the diffusion process was originally run on
    """
    # T = list(I.nodes)
    # S = [v for v in G if v not in T]
    # frontier = nx.node_boundary(G=G, nbunch1=S, nbunch2=T)
    # frontier_idx = [T.index(v) for v in frontier]
    freq = chatter_frequency(I)
    np.fill_diagonal(freq, 0)
    w, v = np.linalg.eig(freq)
    return int(np.argmax((1 / (w + 1))[1 : len(I)]) + 1)


def eigengap(G):
    """Returns the estimated number of clusters of G, based on the Eigengap
    of the normalized graph Laplacian.

    Parameters
    ----------
    G : NetworkX Graph
        The graph to analyze

    Notes
    -----
    The Eigengap heuristic is described in [1]_.

    References
    ----------
    .. [1] U. von Luxburg,
        "A Tutorial on Spectral Clustering"
        Statistics and Computing, 2007
        https://link.springer.com/article/10.1007/s11222-007-9033-z
    """
    warnings.filterwarnings("ignore", category=FutureWarning)

    L = nx.normalized_laplacian_matrix(G).toarray()
    eigenvalues, eigenvectors = np.linalg.eig(L)
    eigenvalues.sort()
    k = np.argmax(np.diff(eigenvalues)) + 1
    return k


def bits_encode_integer(n):
    """Estimates the number of bits required to encode an integer n>=1.

    Parameters
    ----------
    n : int
        an integer at least 1

    Notes
    -----
    Calculation is from Section 4.1 of [1]_.

    References
    ----------
    .. [1] B. A. Prakash, J. Vreeken, C. Faloutsos,
        "Efficiently spotting the starting points of an epidemic in a large graph"
        Knowledge and Information Systems, 2013
        https://link.springer.com/article/10.1007/s10115-013-0671-5
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    l = math.log(2.865064)
    c = math.log(n)
    while c > 0:
        l += c
        c = math.log(c)
    return l


def bits_encode_seed(s, G):
    """Number of bits required to identify a seed set (hypothesized
    infection source set).

    Parameters
    ----------
    s : array-like
        seed set
    G : NetworkX Graph
        The original graph the infection process was run on.

    Notes
    -----
    Calculation is from Section 4.1 of [1]_.

    References
    ----------
    .. [1] B. A. Prakash, J. Vreeken, C. Faloutsos,
        "Efficiently spotting the starting points of an epidemic in a large graph"
        Knowledge and Information Systems, 2013
        https://link.springer.com/article/10.1007/s10115-013-0671-5
    """
    n = len(s)
    return bits_encode_integer(n) + math.log(math.comb(len(G), n))


def bits_encode_ripple(s, G, beta=0.01):
    """Total description length of a seed set and its corresponding maximum likelihood
    propagation ripple.

    Parameters
    ----------
    s : array-like
        seed set
    G : NetworkX Graph
        The original graph the infection process was run on.
    beta : float
        infection probability

    Notes
    -----
    Calculation is from Section 4.3 of [1]_.

    References
    ----------
    .. [1] B. A. Prakash, J. Vreeken, C. Faloutsos,
        "Efficiently spotting the starting points of an epidemic in a large graph"
        Knowledge and Information Systems, 2013
        https://link.springer.com/article/10.1007/s10115-013-0671-5
    """

    def probability_infection(m_d, f_d, d):
        """Probability of m_d nodes being infected in a subset of the frontier.

        Parameters
        ----------
        m_d : int
            number of nodes infected
        f_d :
            number of nodes in a frontier subset F_d
        d : int
            degree

        Notes
        -----
        Calculation is from Section 4.2.3 of [1]_.

        References
        ----------
        .. [1] B. A. Prakash, J. Vreeken, C. Faloutsos,
            "Efficiently spotting the starting points of an epidemic in a large graph"
            Knowledge and Information Systems, 2013
            https://link.springer.com/article/10.1007/s10115-013-0671-5
        """
        p_d = 1 - (1 - beta) ** d  # attack probability in the set
        return math.comb(f_d, m_d) * (p_d**m_d) * (1 - p_d) ** (f_d - m_d)

    def l_frontier(f, infected=s):
        """Calculates the code length for encoding the infectious in the frontier
        set at a snapshot of time.

        Parameters
        ----------
        f : array-like
            frontier set
        infected : array-like
            infected nodes

        Notes
        -----
        Calculation is Equation 3 from Section 4.2.4 of [1]_.

        References
        ----------
        .. [1] B. A. Prakash, J. Vreeken, C. Faloutsos,
            "Efficiently spotting the starting points of an epidemic in a large graph"
            Knowledge and Information Systems, 2013
            https://link.springer.com/article/10.1007/s10115-013-0671-5
        """
        l = 0
        partition = attack_degree_partition(f, infected, G)
        for d in partition:
            f_d = len(partition[d])
            m_d = int(min(math.floor(p_d * (f_d + 1)), f_d))
            if m_d == 0 or f_d == 0:
                continue
            l -= (
                math.log(probability_infection(m_d, f_d, d))
                + m_d * math.log(m_d / f_d)
                + (f_d - m_d) * math.log(1 - m_d / f_d)
            )
        return l

    infected = s
    frontier = set([j for i in infected for j in G.neighbors(i) if j not in infected])
    bits_ripple = 0
    t = 0  # index starts at 0 per p. 42 / Section 4.2.2
    while len(frontier) > 0 and len(infected) < len(G):
        # ripple step, get new frontier
        partition = attack_degree_partition(frontier, infected, G)
        for d in partition:
            f_d = len(partition[d])
            p_d = 1 - (1 - beta) ** d  # attack probability in the set
            n_d = math.floor((f_d / beta + 1) * p_d)

            infected += random.sample(partition[d], min(n_d, f_d))
        frontier = set(
            [j for i in infected for j in G.neighbors(i) if j not in infected]
        )
        infected = list(set(infected))
        bits_ripple += l_frontier(frontier, infected)
        t += 1
    return bits_encode_integer(t) + bits_ripple


def description_length(s, G, beta=0.01):
    """Implements a greedy heuristic to estimate the two-part minimal infection
    description length of a proposed set of infection sources.

    Parameters
    ----------
    s : array-like
        seed set
    G : NetworkX Graph
        The original graph the infection process was run on.
    beta : float
        infection probability

    Notes
    -----
    The minimal description length, as applied to source localization, is introduced
    in [1]_.

    References
    ----------
    .. [1] B. A. Prakash, J. Vreeken, C. Faloutsos,
        "Efficiently spotting the starting points of an epidemic in a large graph"
        Knowledge and Information Systems, 2013
        https://link.springer.com/article/10.1007/s10115-013-0671-5
    """
    return bits_encode_seed(s, G) + bits_encode_ripple(s=s, G=G, beta=0.01)


def chatter_frequency(G, t=None):
    """Implements the Chatter Algorithm described in Notes.

    Parameters
    ----------
    G : NetworkX Graph
        The graph to analyze
    t : int or None (optional)
        number of rounds to complete
        if None, the algorithm runs until every node's message is received by
        every other node at least 5 times.

    Notes
    -----
    Each node starts with a message bank consisting of its own ID.
    For `t` many rounds, each node broadcasts its message bank to its neighbors,
    and all nodes receiving messages append them to their own message bank.
    message_frequency[i][j] is the number of times i received j's message.

    A "naive"/pure message-passing formulation of this would be along the lines of:

    .. code-block:: python

        def chatter_distance_slow(G, t):
            messages = {i:[i] for i in G}
            for _ in range(t):
                new_messages = copy.deepcopy(messages)
                for i in range(len(G)):
                    for j in G.neighbors(i):
                        new_messages[j] += messages[i]
                messages = new_messages
            return messages

    where messages[i].count(j) is the number of times i received j's message. But
    this is very slow and easily re-written as matrix multiplication, as is done
    here.
    """
    warnings.filterwarnings("ignore", category=FutureWarning)

    A = nx.adjacency_matrix(G).toarray()
    message_frequency = scipy.sparse.identity(len(G)).toarray()
    if isinstance(t, type(None)):
        if not nx.is_connected(G):
            return chatter_frequency(G, t=len(G))

        while np.min(message_frequency) < 5:
            for i in range(len(G)):
                message_frequency[i] += A.dot(message_frequency[i])
    else:
        for _ in range(t):
            for i in range(len(G)):
                message_frequency[i] += A.dot(message_frequency[i])
    return message_frequency


def chatter_distance(G, t, u=None, v=None, normalized=True):
    """Invokes the Chatter Algorithm/chatter frequency to obtain chatter distance,
    a graph topology metric.

    Parameters
    ----------
    G :NetworkX Graph
        The graph to analyze
    t : int
        number of rounds to complete
    u : node (optional)
        starting node. if not provided, we return an array of distances
    v : node (optional)
        end node. if not provided, we return an array of distances
    normalized : bool
        if True, all distances are scaled to have a max value of 1

    Notes
    -----
    The chatter distance between nodes `u` and `v` reflects the difficulty node `u`
    is expected to have in transmitting a message to node `v`.
    """
    message_frequency = chatter_frequency(G, t)
    distance = 1 / message_frequency
    if normalized:
        distance /= np.max(distance)
    if isinstance(u, type(None)) and isinstance(v, type(None)):
        return distance
    if isinstance(v, type(None)):
        return distance[u]
    if isinstance(u, type(None)):
        return distance[:][v]
    return distance[u][v]
