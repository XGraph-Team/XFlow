import os, sys

sys.path.insert(0, os.getcwd())

from unittest import TestCase

import pytest
import networkx as nx
import numpy as np
import random

import cosasi


class TestEarliestInfectionFirst(TestCase):
    def setUp(self):
        self.G = nx.fast_gnp_random_graph(100, 0.25)
        contagion = cosasi.StaticNetworkContagion(
            G=self.G, model="si", infection_rate=0.01, number_infected=1
        )
        contagion.forward(50)
        self.t = 20
        self.I = contagion.get_infected_subgraph(self.t)
        self.observers = contagion.get_observers(10)
        return None

    def test_earliest_infection_first_disconnected(self):
        H = nx.disjoint_union(self.G, self.G)
        with pytest.raises(ValueError):
            cosasi.single_source.earliest_infection_first(
                I=self.G, G=H, observer_dict=self.observers
            )

    def test_earliest_infection_first(self):
        result = cosasi.source_inference.single_source.earliest_infection_first(
            I=self.I, G=self.G, observer_dict=self.observers
        )
        assert isinstance(
            result, cosasi.source_inference.source_results.SingleSourceResult
        )
        result_data = result.data["scores"]
        assert isinstance(result_data, dict)
        for i in result_data.keys():
            assert i in self.G.nodes()
            assert isinstance(result_data[i], (float, int)) and result_data[i] > 0
