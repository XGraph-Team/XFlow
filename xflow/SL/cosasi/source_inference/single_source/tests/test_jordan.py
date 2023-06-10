import os, sys

sys.path.insert(0, os.getcwd())

from unittest import TestCase

import pytest
import networkx as nx
import numpy as np

import cosasi


class TestJordan(TestCase):
    def setUp(self):
        self.G = nx.random_tree(n=500, seed=0)
        contagion = cosasi.StaticNetworkContagion(
            G=self.G, model="si", infection_rate=0.1, number_infected=1
        )
        contagion.forward(50)
        self.t = 25
        self.I = contagion.get_infected_subgraph(self.t)
        return None

    def test_jordan_centrality(self):
        result = cosasi.source_inference.single_source.jordan_centrality(self.I, self.G)
        # type check
        assert isinstance(
            result, cosasi.source_inference.source_results.SingleSourceResult
        )
        # soft eccentricity values should either be -inf or in [0, 1]
        noninf_vals = [i for i in result.data["scores"].values() if i != -np.inf]
        assert all(0 <= val <= 1 for val in noninf_vals)
        # confirm the set of nodes w/ highest score is the infection graph center
        center = list(nx.center(self.I))
        result_center = [
            i
            for i in result.data["scores"].keys()
            if result.data["scores"][i] == max(result.data["scores"].values())
        ]
        assert sorted(center) == sorted(result_center)
