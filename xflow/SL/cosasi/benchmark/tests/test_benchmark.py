import os, sys

sys.path.insert(0, os.getcwd())

import pytest
from unittest import TestCase
import networkx as nx
import numpy as np

import cosasi


class Test_BenchmarkFromSimulation(TestCase):
    def setUp(self):
        self.number_infected_init = 3
        self.sim_steps = 100
        self.G = nx.fast_gnp_random_graph(100, 0.25)
        self.contagion = cosasi.StaticNetworkContagion(
            G=self.G,
            model="si",
            infection_rate=0.01,
            number_infected=self.number_infected_init,
        )
        self.contagion.forward(self.sim_steps)
        self.t = 15
        return None

    def test_inputs_contagion(self):
        with pytest.raises((AttributeError, ValueError)):
            cosasi.BenchmarkFromSimulation(
                contagion="BAD INPUT", information_type="single snapshot", t=self.t
            )
        benchmark = cosasi.BenchmarkFromSimulation(
            contagion=self.contagion, information_type="single snapshot", t=self.t
        )
        benchmark.go()
        assert True

    def test_inputs_information_type(self):
        with pytest.raises(NotImplementedError):
            cosasi.BenchmarkFromSimulation(
                contagion=self.contagion, information_type="BAD INPUT", t=self.t
            )
        with pytest.raises(ValueError):
            cosasi.BenchmarkFromSimulation(
                contagion=self.contagion, information_type="observers", t=self.t
            )
        with pytest.raises(ValueError):
            cosasi.BenchmarkFromSimulation(
                contagion=self.contagion,
                information_type="observers",
                t=self.t,
                observers="BAD INPUT",
            )
        benchmark = cosasi.BenchmarkFromSimulation(
            contagion=self.contagion,
            information_type="observers",
            t=self.t,
            observers=2,
        )
        # benchmark.go()
        assert True
        benchmark = cosasi.BenchmarkFromSimulation(
            contagion=self.contagion,
            information_type="observers",
            t=self.t,
            observers=[0, 1],
        )
        # benchmark.go()
        assert True
        benchmark = cosasi.BenchmarkFromSimulation(
            contagion=self.contagion, information_type="single snapshot", t=self.t
        )
        benchmark.go()
        assert True

    def test_inputs_t(self):
        with pytest.raises(ValueError):
            cosasi.BenchmarkFromSimulation(
                contagion=self.contagion,
                information_type="single snapshot",
                t="BAD INPUT",
            )
        with pytest.raises(ValueError):
            # invalid step
            cosasi.BenchmarkFromSimulation(
                contagion=self.contagion,
                information_type="single snapshot",
                t=self.sim_steps + 1,
            )
        benchmark = cosasi.BenchmarkFromSimulation(
            contagion=self.contagion, information_type="single snapshot", t=self.t
        )
        benchmark.go()
        assert True

    def test_go_output(self):
        benchmark = cosasi.BenchmarkFromSimulation(
            contagion=self.contagion, information_type="single snapshot", t=self.t
        )
        results = benchmark.go()
        assert isinstance(results, dict)
        results_keys = results.keys()
        assert all(isinstance(k, str) for k in results_keys)
        assert all(isinstance(results[k], dict) for k in results_keys)
        assert all(
            isinstance(
                results[k]["source result"],
                (
                    cosasi.source_inference.source_results.SingleSourceResult,
                    cosasi.source_inference.source_results.MultiSourceResult,
                ),
            )
            for k in results_keys
        )


class Test_BenchmarkFromDetails(TestCase):
    def setUp(self):
        self.number_infected_init = 3
        self.sim_steps = 100
        self.G = nx.fast_gnp_random_graph(100, 0.25)
        self.contagion = cosasi.StaticNetworkContagion(
            G=self.G,
            model="si",
            infection_rate=0.01,
            number_infected=self.number_infected_init,
        )
        self.contagion.forward(self.sim_steps)
        self.t = 15
        self.I = self.contagion.get_infected_subgraph(step=self.t)
        self.true_source = self.contagion.get_source()
        return None

    def test_inputs_true_source(self):
        with pytest.raises(ValueError):
            benchmark = cosasi.BenchmarkFromDetails(
                true_source="BAD INPUT",
                G=self.G,
                I=self.I,
                t=self.t,
                number_sources=self.number_infected_init,
                information_type="single snapshot",
            )
        benchmark = cosasi.BenchmarkFromDetails(
            true_source=self.true_source,
            G=self.G,
            I=self.I,
            t=self.t,
            number_sources=self.number_infected_init,
            information_type="single snapshot",
        )
        benchmark.go()
        assert True

    def test_inputs_G(self):
        with pytest.raises(ValueError):
            benchmark = cosasi.BenchmarkFromDetails(
                true_source=self.true_source,
                G="BAD INPUT",
                I=self.I,
                t=self.t,
                number_sources=self.number_infected_init,
                information_type="single snapshot",
            )
        benchmark = cosasi.BenchmarkFromDetails(
            true_source=self.true_source,
            G=self.G,
            I=self.I,
            t=self.t,
            number_sources=self.number_infected_init,
            information_type="single snapshot",
        )
        benchmark.go()
        assert True

    def test_inputs_I(self):
        with pytest.raises(ValueError):
            benchmark = cosasi.BenchmarkFromDetails(
                true_source=self.true_source,
                G=self.G,
                I="BAD INPUT",
                t=self.t,
                number_sources=self.number_infected_init,
                information_type="single snapshot",
            )
        benchmark = cosasi.BenchmarkFromDetails(
            true_source=self.true_source,
            G=self.G,
            I=self.I,
            t=self.t,
            number_sources=self.number_infected_init,
            information_type="single snapshot",
        )
        benchmark.go()
        assert True

    def test_inputs_t(self):
        with pytest.raises(ValueError):
            benchmark = cosasi.BenchmarkFromDetails(
                true_source=self.true_source,
                G=self.G,
                I=self.I,
                t="BAD INPUT",
                number_sources=self.number_infected_init,
                information_type="single snapshot",
            )
        benchmark = cosasi.BenchmarkFromDetails(
            true_source=self.true_source,
            G=self.G,
            I=self.I,
            t=self.t,
            number_sources=self.number_infected_init,
            information_type="single snapshot",
        )
        benchmark.go()
        assert True

    def test_inputs_number_sources(self):
        with pytest.raises(TypeError):
            benchmark = cosasi.BenchmarkFromDetails(
                true_source=self.true_source,
                G=self.G,
                I=self.I,
                t=self.t,
                number_sources="BAD INPUT",
                information_type="single snapshot",
            )
        benchmark = cosasi.BenchmarkFromDetails(
            true_source=self.true_source,
            G=self.G,
            I=self.I,
            t=self.t,
            number_sources=self.number_infected_init,
            information_type="single snapshot",
        )
        benchmark.go()
        assert True

    def test_get_namespaces(self):
        # single source should not have any multisource algorithms
        benchmark = cosasi.BenchmarkFromDetails(
            true_source=self.true_source,
            G=self.G,
            I=self.I,
            t=self.t,
            number_sources=1,
            information_type="single snapshot",
        )
        namespaces = [n.__name__ for n in benchmark.get_namespaces()]
        for n in namespaces:
            if "fast_multisource" in n:
                assert False
        assert True
        # multi-source should have multisource algorithms
        benchmark = cosasi.BenchmarkFromDetails(
            true_source=self.true_source,
            G=self.G,
            I=self.I,
            t=self.t,
            number_sources=3,
            information_type="single snapshot",
        )
        namespaces = [n.__name__ for n in benchmark.get_namespaces()]
        temp = False
        for n in namespaces:
            if "fast_multisource" in n:
                temp = True
                break
        assert temp

    def test_go_output(self):
        benchmark = cosasi.BenchmarkFromDetails(
            true_source=self.true_source,
            G=self.G,
            I=self.I,
            t=self.t,
            number_sources=None,
            information_type="single snapshot",
        )
        results = benchmark.go()
        assert isinstance(results, dict)
        results_keys = results.keys()
        assert all(isinstance(k, str) for k in results_keys)
        assert all(isinstance(results[k], dict) for k in results_keys)
        assert all(
            isinstance(
                results[k]["source result"],
                (
                    cosasi.source_inference.source_results.SingleSourceResult,
                    cosasi.source_inference.source_results.MultiSourceResult,
                ),
            )
            for k in results_keys
        )

    def test_go_with_observers(self):
        G = nx.fast_gnp_random_graph(100, 0.25)
        contagion = cosasi.StaticNetworkContagion(
            G=G, model="si", infection_rate=0.01, number_infected=1
        )
        contagion.forward(100)
        I = contagion.get_infected_subgraph(step=25)
        observers = contagion.get_observers(10)
        true_source = contagion.get_source()
        benchmark = cosasi.BenchmarkFromDetails(
            true_source=true_source,
            G=G,
            I=I,
            t=15,
            number_sources=len(true_source),
            information_type="observers",
            observer_dict=observers,
        )
        results = benchmark.go()
        assert "single-source earliest infection first" in results.keys()
        assert "single-source lisn" not in results.keys()
