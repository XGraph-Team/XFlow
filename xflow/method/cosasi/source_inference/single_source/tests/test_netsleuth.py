import os, sys

sys.path.insert(0, os.getcwd())

from unittest import TestCase

import pytest
import networkx as nx
import numpy as np
import random
import math

import cosasi


class TestNETSLEUTH(TestCase):
    def setUp(self):
        self.G = nx.random_tree(n=500, seed=0)
        contagion = cosasi.StaticNetworkContagion(
            G=self.G, model="si", infection_rate=0.1, number_infected=1
        )
        contagion.forward(50)
        self.t = 25
        self.I = contagion.get_infected_subgraph(self.t)
        return None

    def test_netsleuth(self):
        result = cosasi.source_inference.single_source.netsleuth(self.I, self.G)
        assert isinstance(
            result, cosasi.source_inference.source_results.SingleSourceResult
        )
        noninf_vals = [i for i in result.data["scores"].values() if i != -np.inf]
        assert len(noninf_vals) == len(self.I)
