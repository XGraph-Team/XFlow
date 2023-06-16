import os, sys

sys.path.insert(0, os.getcwd())

from unittest import TestCase

import pytest
import networkx as nx
import numpy as np
import random

import cosasi


class TestLISN(TestCase):
    def setUp(self):
        self.G = nx.random_tree(n=500, seed=0)
        contagion = cosasi.StaticNetworkContagion(
            G=self.G, model="si", infection_rate=0.1, number_infected=1
        )
        contagion.forward(50)
        self.t = 25
        self.I = contagion.get_infected_subgraph(self.t)
        return None

    def test_distance_prob(self):
        # for constant distance, probability should weakly increase with time
        last_prob = -np.inf
        n = random.randint(1, 10)
        for t in range(1, 10):
            prob = cosasi.source_inference.single_source.distance_prob(t, n, 0.05)
            assert prob >= last_prob
            last_prob = prob
        # for constant time, probability should weakly decrease with distance
        last_prob = np.inf
        t = random.randint(1, 10)
        for n in range(1, 10):
            prob = cosasi.source_inference.single_source.distance_prob(t, n, 0.05)
            assert prob <= last_prob
            last_prob = prob

    def test_lisn(self):
        result = cosasi.source_inference.single_source.lisn(self.I, self.G, self.t)
        # type check
        assert isinstance(
            result, cosasi.source_inference.source_results.SingleSourceResult
        )
        # -inf only for nodes outside infection subgraph
        vals = list(result.data["scores"].values())
        noninf_vals = [i for i in result.data["scores"].values() if i != -np.inf]
        assert len(noninf_vals) == len(self.I) and len(vals) == len(self.G)
        # scores are log probabilities
        assert -np.inf <= max(noninf_vals) <= max(noninf_vals) <= 0
