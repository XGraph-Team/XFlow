import os, sys

sys.path.insert(0, os.getcwd())

from unittest import TestCase

import pytest
import networkx as nx
import numpy as np
import random

import cosasi


class TestRumorCentrality(TestCase):
    def setUp(self):
        self.G = nx.random_tree(n=500, seed=0)
        contagion = cosasi.StaticNetworkContagion(
            G=self.G, model="si", infection_rate=0.1, number_infected=1
        )
        contagion.forward(50)
        self.t = 25
        self.I = contagion.get_infected_subgraph(self.t)
        return None

    def test_rumor_centrality_root(self):
        for _ in range(5):
            v = random.choice(list(self.I.nodes()))
            result_v = cosasi.single_source.rumor_centrality_root(self.I, v, False)
            assert isinstance(result_v, (int, float)) and result_v > 0
            result_dict = cosasi.single_source.rumor_centrality_root(self.I, v, True)
            for u in result_dict.keys():
                assert u in self.I.nodes()
                assert result_dict[u] > 0
        return None

    def test_rumor_centrality(self):
        with pytest.raises(ValueError):
            cosasi.single_source.rumor_centrality(self.I, self.G, "BAD INPUT")
        result = cosasi.single_source.rumor_centrality(
            self.I, self.G, None, False, False
        )
        assert isinstance(
            result, cosasi.source_inference.source_results.SingleSourceResult
        )
        result_data = result.data["scores"]
        assert isinstance(result_data, dict)
        for i in result_data.keys():
            assert i in self.G.nodes()
            assert isinstance(result_data[i], (float, int)) and result_data[i] > 0


    def test_rumor_centrality_root_example(self):
        """Verifies worked example from Section III.A of [1]_.

        References
        ----------
        .. [1] S., Devavrat and T. Zaman,
            "Rumors in a network: Who's the culprit?."
            IEEE Transactions on Information Theory, 2011
            https://devavrat.mit.edu/wp-content/uploads/2017/10/Rumors-in-a-network-whos-the-culprit.pdf
        """
        I = nx.Graph()
        I.add_edges_from([(1, 2), (1, 3), (2, 4), (2, 5)])
        assert (
            cosasi.single_source.rumor_centrality_root(I, 1, False)
            == cosasi.single_source.rumor_centrality_root(I, 1, True)[1]
            == 8
        )
        # assert cosasi.single_source.rumor_centrality_root(I, 1, True)[1] == 8
