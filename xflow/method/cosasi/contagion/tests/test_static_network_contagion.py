import os, sys
import collections

sys.path.insert(0, os.getcwd())

import pytest
from unittest import TestCase
import networkx as nx
import numpy as np

import cosasi


class Test_StaticNetworkContagion(TestCase):
    def setUp(self):
        self.number_infected_init = 10
        self.sim_steps = 10
        self.G = nx.fast_gnp_random_graph(200, 0.25)
        self.contagion = cosasi.StaticNetworkContagion(
            G=self.G,
            model="si",
            infection_rate=0.1,
            number_infected=self.number_infected_init,
        )
        self.contagion.forward(self.sim_steps)
        return None

    def test_argument_exceptions(self):
        with pytest.raises(ValueError):
            # G must be a NetworkX graph
            cosasi.StaticNetworkContagion(G="BAD INPUT", model="si", infection_rate=0.1)
        with pytest.raises(NotImplementedError):
            # model must be "sir", "si", or "sis"
            cosasi.StaticNetworkContagion(
                G=self.G, model="BAD INPUT", infection_rate=0.1
            )
        with pytest.raises(ValueError):
            # infection_rate must be between 0 and 1
            cosasi.StaticNetworkContagion(G=self.G, model="si", infection_rate=10)
        with pytest.raises(ValueError):
            # recovery_rate must be between 0 and 1
            cosasi.StaticNetworkContagion(
                G=self.G, model="si", infection_rate=0.1, recovery_rate=10
            )
        with pytest.raises(ValueError):
            # can only provide one of fraction_infected, number_infected
            cosasi.StaticNetworkContagion(
                G=self.G,
                model="si",
                infection_rate=0.1,
                fraction_infected=0.1,
                number_infected=self.number_infected_init,
            )
        for m in ["sir", "sis"]:
            with pytest.raises(ValueError):
                # requires recovery rate
                cosasi.StaticNetworkContagion(G=self.G, model=m, infection_rate=0.1)
            cosasi.StaticNetworkContagion(
                G=self.G, model=m, infection_rate=0.1, recovery_rate=0.05
            )
            assert True

    def test_fraction_infected(self):
        contagion = cosasi.StaticNetworkContagion(
            G=self.G,
            model="si",
            infection_rate=0.1,
            fraction_infected=self.number_infected_init / len(self.G),
        )
        contagion.forward(5)
        assert self.number_infected_init == len(contagion.get_source())

    def test_get_infected_indices(self):
        assert len(self.contagion.get_infected_indices()) == self.number_infected_init
        temp_contagion = cosasi.StaticNetworkContagion(
            G=self.G,
            model="si",
            infection_rate=0.1,
            fraction_infected=None,
            number_infected=None,
        )
        temp_contagion.forward()
        assert len(temp_contagion.get_infected_indices()) == 1
        return None

    def test_forward(self):
        assert len(self.contagion.history) == self.sim_steps
        return None

    def test_reset_sim(self):
        self.contagion.reset_sim()
        assert len(self.contagion.history) == 0
        self.contagion.forward(self.sim_steps)
        return None

    def test_get_infected_subgraph(self):
        sg = self.contagion.get_infected_subgraph(step=self.sim_steps - 1)
        assert isinstance(sg, nx.Graph)
        assert len(sg) == len(
            self.contagion.get_infected_indices(step=self.sim_steps - 1)
        )
        assert set(sg.nodes) == set(
            self.contagion.get_infected_indices(step=self.sim_steps - 1)
        )  # sets are unordered
        return None

    def test_get_observers(self):
        num_observers = 5
        self.contagion.forward(steps=100)
        observers = self.contagion.get_observers(observers=num_observers)
        assert len(observers) == num_observers  # check size
        for i in observers.keys():
            assert i in self.G.nodes
            # check types
            assert isinstance(observers[i], (int, float, type(None)))
            if isinstance(observers[i], float):
                observers[i] == np.inf
        return None

    def test_get_source(self):
        source_verts = self.contagion.get_source()
        assert isinstance(source_verts, list)
        assert len(source_verts) <= len(self.G)
        source_graph = self.contagion.get_source(return_subgraph=True)
        assert isinstance(source_graph, nx.Graph)
        assert set(source_graph.nodes) == set(source_verts)
        return None

    def test_get_frontier(self):
        s = 15
        G = nx.fast_gnp_random_graph(100, 0.25)
        contagion = cosasi.StaticNetworkContagion(
            G=G, model="si", infection_rate=0.01, number_infected=3
        )
        contagion.forward(500)
        I = contagion.get_infected_subgraph(step=s)
        frontier = contagion.get_frontier(step=s)
        assert isinstance(frontier, (list, set))  # basic type checking
        assert all(
            [v in I for v in frontier]
        )  # frontier is a subset of infection subgraph
        beyond_frontier = []
        for i in I:
            if i not in frontier:
                # every node not in the frontier has all neighbors in I
                assert all([v in I for v in G.neighbors(v)])
        # frontier at step 0 should just be the initially-infected indices
        frontier_0 = contagion.get_frontier(step=0)
        assert collections.Counter(frontier_0) == collections.Counter(
            contagion.get_source()
        )
        # when the graph is saturated/maximally-infected, frontier should be empty
        largest_cc_size = len(max(nx.connected_components(G), key=len))
        while len(contagion.get_infected_indices(step=s)) < largest_cc_size:
            s += 1
        assert contagion.get_frontier(step=s) == set()
