import os, sys

sys.path.insert(0, os.getcwd())

from unittest import TestCase

import pytest
import networkx as nx
import numpy as np
import random
import math

import cosasi


class TestShortFatTree(TestCase):
    def setUp(self):
        self.G = nx.random_tree(n=500, seed=0)
        contagion = cosasi.StaticNetworkContagion(
            G=self.G, model="si", infection_rate=0.1, number_infected=1
        )
        contagion.forward(50)
        self.t = 25
        self.I = contagion.get_infected_subgraph(self.t)
        return None

    def test_weighted_boundary_node_degree(self):
        # basic type check
        wbnd = cosasi.source_inference.single_source.weighted_boundary_node_degree(
            self.I, self.G, random.choice(list(self.I.nodes()))
        )
        assert isinstance(wbnd, (int, float))
        # double-check worked example
        G = nx.Graph()
        G.add_edges_from(
            [
                (1, 2),
                (2, 5),
                (2, 6),
                (2, 7),
                (1, 4),
                (4, 8),
                (4, 9),
                (4, 10),
                (1, 3),
                (3, 11),
            ]
        )
        I = G.subgraph([1, 2, 3, 4, 5])
        wbnd_1 = cosasi.source_inference.single_source.weighted_boundary_node_degree(
            I, G, 1, abs(math.log(0.5))
        )
        assert wbnd_1 == 0
        (
            wbnd_2,
            v_boundary,
        ) = cosasi.source_inference.single_source.weighted_boundary_node_degree(
            I, G, 2, abs(math.log(0.5)), True
        )
        assert sorted(v_boundary) == [3, 4]
        assert wbnd_2 > wbnd_1

    def test_short_fat_tree(self):
        result = cosasi.source_inference.single_source.short_fat_tree(self.I, self.G)
        assert isinstance(
            result, cosasi.source_inference.source_results.SingleSourceResult
        )
        noninf_vals = [i for i in result.data["scores"].values() if i != -np.inf]
        assert len(noninf_vals) <= len(
            self.I
        )  # score vals are wbnd, these are checked in test_weighted_boundary_node_degree
