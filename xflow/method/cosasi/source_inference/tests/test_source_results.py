import os, sys
import pytest
import itertools
import random

sys.path.insert(0, os.getcwd())

from unittest import TestCase

import networkx as nx
import numpy as np

import cosasi

from ..source_results import SourceResult, SingleSourceResult, MultiSourceResult, node_set_distance


def test_node_set_distance():
    G = nx.karate_club_graph()

    # sets are individual nodes
    assert node_set_distance(5, 2, G) == 2
    # mixed
    assert node_set_distance(5, [2, 3], G) == 6
    assert node_set_distance([5, 6, 7], 2, G) == 7
    # bother iterable
    assert node_set_distance([5, 6], [2, 3], G) == 4
    # overlapping
    assert node_set_distance([5, 6], [5, 6], G) == 0
    assert node_set_distance([5, 6], [2, 6], G) == node_set_distance(5, 2, G) == 2


class Test_SourceResult(TestCase):
    def setUp(self):
        self.inference_method = "rumor centrality"
        self.scores = {1: 1, 2: 10, 3: 0.025}
        self.G = nx.fast_gnp_random_graph(50, 0.25)
        self.result = SourceResult(
            inference_method=self.inference_method,
            scores=self.scores,
            source_type="single-source",
            G=self.G,
        )
        return None

    def test_rank(self):
        ranked = self.result.rank()
        assert self.result.rank() == [2, 1, 3]

    def test_topn(self):
        with pytest.raises(ValueError):
            assert self.result.topn("BAD INPUT")
        assert self.result.topn(n=1) == [2]

    def test_bad_graph_input(self):
        with pytest.raises(ValueError):
            assert SourceResult(
                inference_method=self.inference_method,
                scores=self.scores,
                source_type="single-source",
                G="BAD INPUT",
            )

    def test_bad_source_type_input(self):
        with pytest.raises(ValueError):
            assert SourceResult(
                inference_method=self.inference_method,
                scores=self.scores,
                source_type="BAD INPUT",
                G=self.G,
            )


class Test_SingleSourceResult(TestCase):
    def setUp(self):
        self.inference_method = "rumor centrality"
        self.scores = {1: 1, 2: 10, 3: 0.025}
        self.G = nx.fast_gnp_random_graph(50, 0.25)
        self.result = SingleSourceResult(
            inference_method=self.inference_method,
            scores=self.scores,
            source_type="single-source",
            G=self.G,
        )
        return None

    def test_get_rank(self):
        assert self.result.get_rank(2) == 1
        assert self.result.get_rank(3) == 3
        with pytest.raises(ValueError):
            assert self.result.get_rank("BAD INPUT")

    def test_bad_graph_input(self):
        with pytest.raises(ValueError):
            assert SingleSourceResult(
                inference_method=self.inference_method,
                scores=self.scores,
                source_type="single-source",
                G="BAD INPUT",
            )


class Test_MultiSourceResult(TestCase):
    def setUp(self):
        self.inference_method = "fast multi-source jordan centrality"
        self.scores = {}
        self.G = nx.fast_gnp_random_graph(50, 0.25)
        for s in list(itertools.combinations(range(5), 2)):
            self.scores[s] = random.random()
        self.result = MultiSourceResult(
            inference_method=self.inference_method,
            scores=self.scores,
            source_type="multi-source",
            G=self.G,
        )
        return None

    def test_get_rank(self):
        max_key = max(self.scores, key=self.scores.get)
        assert self.result.get_rank(max_key) == 1

    def test_bad_graph_input(self):
        with pytest.raises(ValueError):
            assert MultiSourceResult(
                inference_method=self.inference_method,
                scores=self.scores,
                source_type="single-source",
                G="BAD INPUT",
            )
