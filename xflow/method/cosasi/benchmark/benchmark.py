import random
import os, sys
import json

sys.path.insert(0, os.getcwd())

import numpy as np
import networkx as nx

import cosasi

MODULE_PATH = __file__[: -len("benchmark.py")]
MODULE_PATH = (
    MODULE_PATH
    if len(MODULE_PATH) > 0 and (MODULE_PATH[-1] == "/" or MODULE_PATH[-1] == "\\")
    else MODULE_PATH + "/"
)
ALGORITHMS_PATH = MODULE_PATH[: -len("benchmark/")] + "source_inference/"


def _get_relevant_namespaces(
    source_type=None, information_type="single snapshot", epidemic_model=None
):
    """Retrieves the functional names of all applicable source inference algorithms.

    Parameters
    ----------
    source_type : str or None (optional)
        one of None, "single-source", or "multi-source"
        If None, we consider any source type
    information_type : str
        describes the information the source inference algorithm receives
        e.g. "single snapshot"
    epidemic_model : str or None (optional)
        specifies the epidemic model, e.g. SI, SIS, SIR
        if None, ignores this constraint
    """
    valid_namespaces = []
    algorithms_dict = json.load(open(ALGORITHMS_PATH + "algorithm_details.json"))

    if isinstance(source_type, type(None)):
        source_type_iter = list(algorithms_dict.keys())
    else:
        source_type_iter = [source_type]

    for source_type in source_type_iter:
        for alg_name in algorithms_dict[source_type]:
            if not isinstance(epidemic_model, type(None)):
                if (
                    epidemic_model.lower()
                    not in algorithms_dict[source_type][alg_name]["epidemic model"]
                ):
                    continue

            if (
                algorithms_dict[source_type][alg_name]["information type"]
                == information_type
                and algorithms_dict[source_type][alg_name]["status"] == "complete"
            ):
                valid_namespaces.append(
                    eval(algorithms_dict[source_type][alg_name]["namespace"])
                )
    return valid_namespaces


def _get_namespace_params(name, return_defaults=True):
    """Retrieves the names of the parameters and their default values.

    Parameters
    ----------
    name : function
        function namespace
    return_defaults : bool
        if True, also includes
    """
    arg_num = name.__code__.co_argcount
    param_names = name.__code__.co_varnames[:arg_num]

    if not return_defaults:
        return param_names

    params = {}
    if isinstance(name.__defaults__, type(None)):
        defaults = []
    else:
        defaults = list(name.__defaults__)[::-1]
    param_names = param_names[::-1]
    for i in range(len(param_names)):
        if i < len(defaults):
            arg = defaults[i]
        else:
            arg = ""
        params[param_names[i]] = arg
    return params


def _execute_algorithm_from_namespace(name, what_we_know):
    """Runs a source inference algorithm, passing what we know as arguments.

    Parameters
    ----------
    name : function
        function namespace
    what_we_know : dict
        dictionary of arguments we want to pass to the algorithm
    """
    function_args = _get_namespace_params(name=name, return_defaults=True)

    for param in what_we_know:
        if param in function_args:
            function_args[param] = what_we_know[param]

    if "" in function_args.values():
        raise ValueError(
            "Insufficient arguments provided.",
            function_args,
            what_we_know,
            name,
            name.__defaults__,
        )

    return name(**function_args)


class BenchmarkFromDetails:
    """Benchmarking tool using provided class args to pass to algorithms when available.

    Parameters
    ----------
    true_source : node or tuple of nodes
        the true source of the diffusion process
    G : NetworkX Graph
        The original graph the infection process was run on.
        I is a subgraph of G induced by infected vertices at observation time.
    information_type : str
        describes the information the source inference algorithm receives
        e.g. "single snapshot"
    I : NetworkX Graph
        The infection subgraph observed at a particular time step
    t : int
        the timestep corresponding to I
    observer_dict : dict or None (optional)
        takes a dict of observers and the timestamps at which they become infected.
    epidemic_model : str or None (optional)
        specifies the epidemic model, e.g. SI, SIS, SIR
        if None, ignores this constraint
    number_sources : int or None (optional)
        if int, this is the hypothesized number of infection sources
        if None, estimates the number of sources
    infection_rate : float or None (optional)
        Inter-node infection efficiency. If a float, must be in [0,1]
        if None, ignores this parameter
    """

    def __init__(
        self,
        true_source,
        G,
        information_type,
        I=None,
        t=None,
        observer_dict=None,
        epidemic_model=None,
        number_sources=None,
        infection_rate=None,
    ):
        """Benchmarking tool using provided class args to pass to algorithms when available.

        Parameters
        ----------
        true_source : node or tuple of nodes
            the true source of the diffusion process
        G : NetworkX Graph
            The original graph the infection process was run on.
            I is a subgraph of G induced by infected vertices at observation time.
        information_type : str
            describes the information the source inference algorithm receives
            e.g. "single snapshot"
        I : NetworkX Graph
            The infection subgraph observed at a particular time step
        t : int
            the timestep corresponding to I
        observer_dict : dict or None (optional)
            takes a dict of observers and the timestamps at which they become infected.
        epidemic_model : str or None (optional)
            specifies the epidemic model, e.g. SI, SIS, SIR
            if None, ignores this constraint
        number_sources : int or None (optional)
            if int, this is the hypothesized number of infection sources
            if None, estimates the number of sources
        infection_rate : float or None (optional)
            Inter-node infection efficiency. If a float, must be in [0,1]
            if None, ignores this parameter
        """
        self.epidemic_model = epidemic_model
        self.number_sources = number_sources
        self.information_type = information_type
        if isinstance(t, (int, float, type(None))):
            self.t = t
        else:
            raise ValueError("Time parameter must be an integer or float or None")
        self.observer_dict = observer_dict

        if information_type == "single snapshot" and (
            isinstance(I, type(None)) or isinstance(t, type(None))
        ):
            raise ValueError(
                "If information type is single snapshot, we need the infection subgraph and its corresponding timestep"
            )
        if information_type == "observers" and (isinstance(observer_dict, type(None))):
            raise ValueError(
                "If the information type is observers, we need the observer_dict"
            )

        if isinstance(G, nx.classes.graph.Graph):
            self.G = G
        else:
            raise ValueError("G must be a NetworkX graph.")

        if all(v in G for v in true_source):
            self.true_source = true_source
        elif true_source in G:
            self.true_source = true_source
        else:
            raise ValueError("All members of true_source must be in G.")

        if isinstance(I, (nx.classes.graph.Graph, type(None))):
            self.I = I
        else:
            raise ValueError("I must be a NetworkX graph.")

        if (
            isinstance(infection_rate, float) and 0.0 <= infection_rate <= 1.0
        ) or isinstance(infection_rate, type(None)):
            self.infection_rate = infection_rate
        else:
            raise ValueError("Infection rate must be a float between 0 and 1.")

        self.namespaces = self.get_namespaces()
        return None

    def get_namespaces(self):
        """Finds all source localization algorithms applicable to the contagion task
        specified in the class constructor.
        """
        if isinstance(self.number_sources, type(None)):
            source_type = None
        elif self.number_sources > 1:
            source_type = "multi-source"
        elif self.number_sources == 1:
            source_type = "single-source"
        else:
            raise NotImplementedError

        namespaces = _get_relevant_namespaces(
            source_type=source_type,
            information_type=self.information_type,
            epidemic_model=self.epidemic_model,
        )

        return namespaces

    def go(self):
        """Runs all available algorithms with the information we have on hand."""
        result_dict = {}
        what_we_know = {
            "G": self.G,
            "I": self.I,
            "observer_dict": self.observer_dict,
            "t": self.t,
            "number_sources": self.number_sources,
        }
        for alg in self.namespaces:
            result = _execute_algorithm_from_namespace(
                name=alg, what_we_know=what_we_know
            )
            inference_method = result.data["inference method"]["name"]
            source_type = result.data["inference method"]["source_type"]
            result_dict[source_type + " " + inference_method] = {
                "source result": result,
                "evaluation": result.evaluate(true_source=self.true_source),
            }

        return result_dict


class BenchmarkFromSimulation:
    """Benchmarking tool using provided simulation object to pass to algorithms when available.

    Parameters
    ----------
    contagion : cosasi.contagion.static_network_contagion.StaticNetworkContagion
        an already-run contagion object
    t : int
        the timestep corresponding to I
    information_type : str or None (optional)
        describes the information the source inference algorithm receives
        e.g. "single snapshot"
    observers : int or list
        If int, observers specifies the number of observation nodes
        If list, observers specifies the observation nodes directly
    """

    def __init__(self, contagion, t=None, information_type=None, observers=None):
        """Benchmarking tool using provided simulation object to pass to algorithms when available.

        Parameters
        ----------
        contagion : cosasi.contagion.static_network_contagion.StaticNetworkContagion
            an already-run contagion object
        t : int
            the timestep corresponding to I
        information_type : str or None (optional)
            describes the information the source inference algorithm receives
            e.g. "single snapshot"
        observers : int or list
            If int, observers specifies the number of observation nodes
            If list, observers specifies the observation nodes directly
        """
        true_source = contagion.get_source()
        if information_type == "single snapshot":
            if isinstance(t, type(None)):
                raise ValueError("If information type is snapshot, t is required")
            if not isinstance(t, int):
                raise ValueError("t must be an int")
            self.benchmarker = BenchmarkFromDetails(
                true_source=true_source,
                G=contagion.G,
                I=contagion.get_infected_subgraph(step=t),
                t=t,
                epidemic_model=contagion.model,
                number_sources=len(true_source),
                information_type=information_type,
                infection_rate=contagion.infection_rate,
            )
        elif information_type == "observers":
            if isinstance(observers, type(None)):
                raise ValueError(
                    "If information type is observers, the number of observers is required"
                )
            if not isinstance(observers, (int, list)):
                raise ValueError("observers must be an int or a list")
            self.benchmarker = BenchmarkFromDetails(
                true_source=true_source,
                G=contagion.G,
                observer_dict=contagion.get_observers(observers=observers),
                epidemic_model=contagion.model,
                number_sources=len(true_source),
                information_type=information_type,
                infection_rate=contagion.infection_rate,
            )
        else:
            raise NotImplementedError
        return None

    def go(self):
        """Runs all available algorithms with the information we have on hand."""
        return self.benchmarker.go()
