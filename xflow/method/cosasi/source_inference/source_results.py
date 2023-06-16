"""Generic objects for the result of single-source and multi-source localization.

All inference algorithms should return an instance of one of these classes.
"""

import json
from collections import Counter
from collections.abc import Iterable
import itertools

import numpy as np
import networkx as nx

MODULE_PATH = __file__[: -len("source_results.py")]
MODULE_PATH = (
    MODULE_PATH
    if len(MODULE_PATH) > 0 and (MODULE_PATH[-1] == "/" or MODULE_PATH[-1] == "\\")
    else MODULE_PATH + "/"
)


def node_set_distance(s1, s2, G):
    """Implements a distance measure between vertex sets (of possibly different sizes).

    Parameters
    ----------
    s1 : array-like
        first vertex set
    s2 : array-like
        second vertex set
    G : NetworkX Graph
        graph to search on
    """
    perm_scores = {}

    if isinstance(s1, Iterable):
        s1 = list(s1)
    else:
        s1 = [s1]
    if isinstance(s2, Iterable):
        s2 = list(s2)
    else:
        s2 = [s2]

    for s2_perm in itertools.permutations(s2):
        perm_scores[s2_perm] = 0
        for i in range(min(len(s1), len(s2))):
            perm_scores[s2_perm] += nx.shortest_path_length(
                G, source=s1[i], target=s2_perm[i]
            )
        if len(s1) > len(s2):
            for j in range(i, len(s1)):
                min_add = np.inf
                for s in s2_perm:
                    d = nx.shortest_path_length(G, source=s1[j], target=s)
                    if d < min_add:
                        min_add = d
                perm_scores[s2_perm] += min_add
        if len(s2) > len(s1):
            for j in range(i, len(s2_perm)):
                min_add = np.inf
                for s in s1:
                    d = nx.shortest_path_length(G, source=s2_perm[j], target=s)
                    if d < min_add:
                        min_add = d
                perm_scores[s2_perm] += min_add
    return min(perm_scores.values())


class SourceResult:
    """Abstract class outlining response object for the result of a source inference algorithm.

    Parameters
    ----------
    source_type : str
        either "single-source" or "multi-source"
    inference_method : str
        name of the source localization algorithm used
    scores : dict
        per-item scores for ranking, retrieval, etc.
    G : NetworkX Graph
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.
    algorithm_details : bool
        if True, includes relevant information about the source
        inference algorithm used
    reverse : bool (default True)'
        if True, ranks items from highest score to lowest
        if False, ranks items from lowest score to highest
    """

    def __init__(
        self,
        source_type,
        inference_method,
        scores,
        G,
        algorithm_details=True,
        reverse=True,
    ):
        """Abstract class outlining response object for the result of a source inference algorithm.

        Parameters
        ----------
        source_type : str
            either "single-source" or "multi-source"
        inference_method : str
            name of the source localization algorithm used
        scores : dict
            per-item scores for ranking, retrieval, etc.
        G : NetworkX Graph
            The original graph the infection process was run on.
            I is a subgraph of G induced by infected vertices at observation time.
        algorithm_details : bool
            if True, includes relevant information about the source
            inference algorithm used
        reverse : bool (default True)'
            if True, ranks items from highest score to lowest
            if False, ranks items from lowest score to highest
        """
        if not isinstance(G, nx.classes.graph.Graph):
            raise ValueError("G must be a NetworkX graph.")
        else:
            self.G = G

        source_type = source_type.lower()
        if source_type not in ["single-source", "multi-source"]:
            raise ValueError("Source type must be single- or multi-source.")
        self.data = {
            "scores": scores,
            "inference method": {"name": inference_method, "source_type": source_type},
            "G": G,
        }
        if algorithm_details:
            algorithms = json.load(open(MODULE_PATH + "algorithm_details.json"))
            for k in algorithms[source_type][inference_method]:
                self.data["inference method"][k] = algorithms[source_type][
                    inference_method
                ][k]
        self.reverse = reverse
        return None

    def rank(self):
        """Rank nodes by score.

        Returns
        -------
        list of item indices
        """
        scores = self.data["scores"]
        return sorted(scores, key=scores.get, reverse=self.reverse)

    def topn(self, n=1):
        """Returns the top n item indices by rank.

        Rank can be highest-first (reverse==True) or lowest-first (reverse==False)

        Parameters
        ----------
        n : int
            number of item indices to return

        Returns
        -------
        list of item indices
        """
        if not isinstance(n, int):
            raise ValueError("n must be an integer.")
        rank = self.rank()
        return rank[:n]

    def evaluate_solution_rank(self, true_source):
        """Finds the rank of the true source, by the algorithm's scoring protocol.

        Parameters
        ----------
        true_source : graph index - str, int, etc.
            the actual source node
        """
        single_source = len(self.topn(n=1)) == 1
        if isinstance(true_source, (list, tuple)) and len(true_source) == 1:
            true_source = true_source[0]

        return self.get_rank(true_source, soft_rank=True)

    def evaluate_distance(self, true_source):
        """Finds the shortest path length between each node in the solution set and the
        true souce.

        Parameters
        ----------
        true_source : tuple
            the actual source set
        """
        eval_scores = {h: np.inf for h in self.data["scores"]}
        for s in eval_scores.keys():
            eval_scores[s] = node_set_distance(G=self.G, s1=s, s2=true_source)
        return eval_scores

    def evaluate(self, true_source):
        """Runs evaluation algorithms and returns a dictionary of results.

        Parameters
        ----------
        true_source : graph index - str, int, etc.
            the actual source node
        """
        dist = self.evaluate_distance(true_source=true_source)
        top_sol = self.topn(n=1)[0]
        rank = self.evaluate_solution_rank(true_source=true_source)
        evaluation_results = {
            "true source": true_source,
            "distance": {
                "top score's distance": {top_sol: dist[top_sol]},
                "all distances": dist,
            },
            "rank": rank,
            "rank %": rank / len(self.data["scores"]),
        }
        return evaluation_results


class SingleSourceResult(SourceResult):
    """Response object for the result of single-source inference.

    Parameters
    ----------
    inference_method : str
        name of the source localization algorithm used
    scores : dict
        per-node scores for ranking, retrieval, etc.
    algorithm_details : bool
        if True, includes relevant information about the source
        inference algorithm used
    reverse : bool (default True)'
        if True, ranks items from highest score to lowest
        if False, ranks items from lowest score to highest
    """

    def __init__(self, *args, **kwargs):
        """Response object for the result of single-source inference.

        Parameters
        ----------
        inference_method : str
            name of the source localization algorithm used
        scores : dict
            per-node scores for ranking, retrieval, etc.
        algorithm_details : bool
            if True, includes relevant information about the source
            inference algorithm used
        reverse : bool (default True)'
            if True, ranks items from highest score to lowest
            if False, ranks items from lowest score to highest
        """
        super().__init__(*args, **kwargs)
        return None

    def get_rank(self, v, soft_rank=False):
        """Returns the rank of vertex (1 = "best")

        Parameters
        ----------
        v : graph index - str, int, etc.
            vertex of interest
        soft_rank : bool
            if True and v is not in the list of hypotheses, returns 1 more
            than the number of hypotheses

        Returns
        -------
        int
        """
        rank = self.rank()

        if soft_rank and v not in rank:
            return len(rank) + 1
        return rank.index(v) + 1


class MultiSourceResult(SourceResult):
    """Response object for the result of mutli-source inference.

    Parameters
    ----------
    inference_method : str
        name of the source localization algorithm used
    scores : dict
        per-item scores for ranking, retrieval, etc.
    algorithm_details : bool
        if True, includes relevant information about the source
        inference algorithm used
    reverse : bool (default True)'
        if True, ranks items from highest score to lowest
        if False, ranks items from lowest score to highest
    """

    def __init__(self, *args, **kwargs):
        """Response object for the result of mutli-source inference.

        Parameters
        ----------
        inference_method : str
            name of the source localization algorithm used
        scores : dict
            per-item scores for ranking, retrieval, etc.
        algorithm_details : bool
            if True, includes relevant information about the source
            inference algorithm used
        reverse : bool (default True)'
            if True, ranks items from highest score to lowest
            if False, ranks items from lowest score to highest
        """
        super().__init__(*args, **kwargs)
        return None

    def get_rank(self, s, soft_rank=False):
        """Returns the rank of the provided node set (1 = "best")

        Parameters
        ----------
        s : list
            node set of graph indices
        soft_rank : bool
            if True and v is not in the list of hypotheses, returns 1 more
            than the number of hypotheses

        Returns
        -------
        int
        """
        rank = self.rank()
        r = 1
        for q in rank:
            if Counter(s) == Counter(q):
                break
            r += 1
        if not soft_rank and r > len(self.data["scores"]):
            raise ValueError("Proposed source set not found among top hypotheses.")
        return r
