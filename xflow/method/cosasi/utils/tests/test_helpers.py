import os, sys

sys.path.insert(0, os.getcwd())

import pytest
import networkx as nx
import numpy as np
import random

from cosasi import utils


def test_list_product():
    l = [1]
    assert utils.list_product(l) == 1
    l += [2]
    assert utils.list_product(l) == 2
    l += [-3]
    assert utils.list_product(l) == -6
    l += [0]
    assert utils.list_product(l) == 0
    return None


def test_longest_list():
    n = 10
    l = []
    for i in range(n):
        l.append(list(range(i)))
    longest = utils.longest_list(l)
    assert longest == list(range(n - 1))


def test_longest_list_len():
    n = 10
    l = []
    for i in range(n):
        l.append(list(range(i)))
    assert utils.longest_list_len(l) == n - 1


def test_soft_eccentricity():
    G = nx.complete_graph(4)
    assert utils.soft_eccentricity(G, 1) < np.inf
    H = nx.disjoint_union(G, G)
    assert utils.soft_eccentricity(H, 1) == np.inf
    G = nx.complete_graph(1)
    assert utils.soft_eccentricity(G, 0) == 1


def test_attack_degree():
    G = nx.complete_graph(4)
    infected = [3]
    for i in range(3):
        assert utils.attack_degree(infected, G, i) == 1


def attack_degree_partition():
    G = nx.gnp_random_graph(50, 0.2)
    node_set = [1, 3, 4]
    infected = [1, 16, 17, 19, 24, 34, 36, 41, 43, 49]
    partition = utils.attack_degree_partition(node_set, infected, G)
    vals = []
    for v in partition.values():
        vals += v
    assert sorted(vals) == sorted(node_set)
    assert max(partition) <= max(G.degree())[1]
