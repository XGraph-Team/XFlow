import os, sys

sys.path.insert(0, os.getcwd())

from unittest import TestCase

import pytest
import networkx as nx
import numpy as np

import cosasi


class TestEstimators(TestCase):
    def setUp(self):
        self.G = self.G = nx.gnp_random_graph(50, 0.2)
        contagion = cosasi.StaticNetworkContagion(
            G=self.G, model="si", infection_rate=0.1, number_infected=1
        )
        contagion.forward(30)
        self.t = 25
        self.I = contagion.get_infected_subgraph(self.t)
        return None

    def test_source_subgraphs(self):
        for i in range(1, 10):
            subgraphs = cosasi.utils.estimators.source_subgraphs(
                self.G, number_sources=i
            )
            assert len(subgraphs) == i

    def test_number_sources(self):
        for method in ["eigengap", "netsleuth", "chatter"]:
            # check that number of sources matches when provided
            for number_sources in range(1, 5):
                n, subgraphs = cosasi.utils.estimators.number_sources(
                    I=self.I,
                    number_sources=number_sources,
                    return_source_subgraphs=True,
                    number_sources_method=method,
                    G=self.G,
                )
                for g in subgraphs:
                    assert type(g) == nx.Graph
                assert n == number_sources
            # estimating numbers as expected
            n, subgraphs = cosasi.utils.estimators.number_sources(
                I=self.I,
                number_sources=None,
                return_source_subgraphs=True,
                number_sources_method=method,
                G=self.G,
            )
            m = cosasi.utils.estimators.number_sources(
                I=self.I,
                number_sources=None,
                return_source_subgraphs=False,
                number_sources_method=method,
                G=self.G,
            )
            assert n == m and (isinstance(n, np.int64) or isinstance(n, int))
            # just return number_sources back
            n = 2
            m = cosasi.utils.estimators.number_sources(
                I=self.I,
                number_sources=n,
                return_source_subgraphs=False,
                number_sources_method=method,
                G=self.G,
            )
            assert n == m
        # check error-handling
        with pytest.raises(NotImplementedError):
            assert cosasi.utils.estimators.number_sources(
                self.I,
                number_sources=None,
                return_source_subgraphs=False,
                number_sources_method="BAD INPUT",
            )
        with pytest.raises(ValueError):
            # Need `G` for NETSLEUTH method
            assert cosasi.utils.estimators.number_sources(
                G=None,
                I=self.I,
                number_sources=None,
                return_source_subgraphs=False,
                number_sources_method="netsleuth",
            )
        with pytest.raises(ValueError):
            # Need `G` for chatter method
            assert cosasi.utils.estimators.number_sources(
                G=None,
                I=self.I,
                number_sources=None,
                return_source_subgraphs=False,
                number_sources_method="chatter",
            )
        with pytest.raises(ValueError):
            # Need `G` for chatter method
            assert cosasi.utils.estimators.number_sources(
                G=self.G,
                I=self.I,
                number_sources="BAD INPUT",
                return_source_subgraphs=False,
                number_sources_method="chatter",
            )

    def test_eigengap(self):
        assert isinstance(cosasi.utils.estimators.eigengap(self.G), np.int64)
        # two disjoint complete graphs should have a spectral gap of 2
        K = nx.complete_graph(10)
        H = nx.disjoint_union(K, K)
        assert cosasi.utils.estimators.eigengap(H) == 2

    def test_bits_encode_integer(self):
        last = 0
        for i in range(-10, 10):
            if i < 1:
                with pytest.raises(ValueError):
                    cosasi.utils.estimators.bits_encode_integer(i)
            else:
                # number of bits should increase w/ integer
                bits = cosasi.utils.estimators.bits_encode_integer(i)
                assert bits > last
                last = bits
        assert cosasi.utils.estimators.bits_encode_integer(1) == pytest.approx(1.05259)

    def test_bits_encode_seed(self):
        seed = [1, 2, 3]
        assert cosasi.utils.estimators.bits_encode_seed(
            seed, self.G
        ) > cosasi.utils.estimators.bits_encode_integer(len(seed))

    def test_bits_encode_ripple(self):
        bits_ripple_1 = cosasi.utils.estimators.bits_encode_ripple(
            list(range(1)), self.G
        )
        bits_ripple_2 = cosasi.utils.estimators.bits_encode_ripple(
            list(range(5)), self.G
        )
        assert 0 < min(bits_ripple_1, bits_ripple_2)

    def test_description_length(self):
        seed = [1, 2, 3]
        assert (
            min(
                cosasi.utils.estimators.description_length(seed, self.G),
                cosasi.utils.estimators.description_length(seed, self.G),
            )
            > 0
        )

    def test_chatter_frequency(self):
        message_frequency = cosasi.utils.estimators.chatter_frequency(self.G, 5)
        assert message_frequency.size == len(self.G) * len(self.G)
        assert np.min(message_frequency) >= 0

    def test_chatter_distance(self):
        for t in [1, 5, None]:
            for G in [self.G, nx.disjoint_union(self.G, self.G)]:
                # distances are non-negative
                assert (
                    np.min(
                        cosasi.utils.estimators.chatter_distance(
                            G=G, t=t, normalized=False
                        )
                    )
                    >= 0
                )
                dist = cosasi.utils.estimators.chatter_distance(
                    G=G, t=t, normalized=True
                )
                if (
                    dist[0][1] != dist[0][1]
                    or np.max(dist) != np.max(dist)
                    or np.min(dist) != np.min(dist)
                ):
                    pass
                else:
                    assert dist[0][1] == cosasi.utils.estimators.chatter_distance(
                        G=G, t=t, u=0, v=1, normalized=True
                    )
                    # check normalization
                    assert 1 >= np.max(dist) >= np.min(dist) >= 0
                    # array ops work right
                    assert len(
                        cosasi.utils.estimators.chatter_distance(G=G, t=t, u=0)
                    ) == len(G)
                    assert len(
                        cosasi.utils.estimators.chatter_distance(self.G, 5, v=0)
                    ) == len(G)
                    # should be symmetric
                    for i in range(len(G)):
                        for j in range(len(G)):
                            assert cosasi.utils.estimators.chatter_distance(
                                G=G, t=t, u=i, v=j, normalized=False
                            ) == cosasi.utils.estimators.chatter_distance(
                                G=G, t=t, u=j, v=i, normalized=False
                            )

    def test_chatter(self):
        result = cosasi.utils.estimators.chatter(self.I, self.G)
        assert isinstance(result, int)
        assert result > 0
        assert result <= len(self.I)
