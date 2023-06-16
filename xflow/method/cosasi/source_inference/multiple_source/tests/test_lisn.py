import os, sys

sys.path.insert(0, os.getcwd())

from unittest import TestCase

import pytest
import networkx as nx

import cosasi


class TestLISN(TestCase):
    def setUp(self):
        self.G = nx.complete_graph(n=100)
        contagion = cosasi.StaticNetworkContagion(
            G=self.G, model="si", infection_rate=0.1, number_infected=1
        )
        contagion.forward(50)
        self.t = 25
        self.I = contagion.get_infected_subgraph(self.t)
        return None

    def test_fast_multisource_lisn(self):
        result = cosasi.source_inference.multiple_source.fast_multisource_lisn(
            self.I, self.G, self.t, 3
        )
        assert isinstance(
            result, cosasi.source_inference.source_results.MultiSourceResult
        )
        top5 = result.topn(5)
        assert [len(i) == 3 for i in top5]
        result = cosasi.source_inference.multiple_source.fast_multisource_lisn(
            self.I, self.G, self.t
        )
        l = None
        for k in result.data["scores"].keys():
            if not l:
                l = len(k)
            else:
                assert len(k) == l
