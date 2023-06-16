import random
import numpy as np
import operator

import networkx as nx
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc


class StaticNetworkContagion:
    """A stochastic epidemic process defined on a static network.

    Parameters
    ----------
    G : NetworkX Graph
        The network for the diffusion process to run on
    model : str
        Specifies the epidemic model. Currently handles the following diffusion models:
            - SI (susceptible-infected)
            - SIS (susceptible-infected-susceptible)
            - SIR (susceptible-infected-recovered)
    infection_rate : float
        Inter-node infection efficiency
        must be in [0, 1]
    recovery_rate : float or None
        The recovery rate
        must be in [0, 1] (or None if diffusion model is SI)
    fraction_infected : float or None
        fraction of nodes to initialize as infected (selected uniformly at random)
        if both fraction_infected and number_infected are None, initializes with 1 infected node
    number_infected : float or None
        number of nodes to initialize as infected (selected uniformly at random)
        if both fraction_infected and number_infected are None, initializes with 1 infected node
    seed : integer, random_state, or None (default)
        random number generation state.

    Notes
    -----
    A wrapper for `ndlib` with convenience utilities added.
    """

    def __init__(
        self,
        G,
        model="si",
        infection_rate=0.01,
        recovery_rate=None,
        fraction_infected=None,
        number_infected=None,
        seed=None,
        model_config=None # added by Zhiqian
    ):
        """A stochastic epidemic process defined on a static network.

        Parameters
        ----------
        G : NetworkX Graph
            The network for the diffusion process to run on
        model : str
            Specifies the epidemic model. Currently handles the following diffusion models:
                SI
                SIS
                SIR
        infection_rate : float
            Inter-node infection efficiency
            must be in [0, 1]
        recovery_rate : float or None
            The recovery rate
            must be in [0, 1] (or None if diffusion model is SI)
        fraction_infected : float or None
            fraction of nodes to initialize as infected (selected uniformly at random)
            if both fraction_infected and number_infected are None, initializes with 1 infected node
        number_infected : float or None
            number of nodes to initialize as infected (selected uniformly at random)
            if both fraction_infected and number_infected are None, initializes with 1 infected node
        seed : integer, random_state, or None (default)
            random number generation state.

        Notes
        -----
        A wrapper for `ndlib` with convenience utilities added.
        """
        self.model = model.lower()
        self.seed = seed
        self.model_config = model_config if model_config else mc.Configuration()  # added by Zhiqian


        if not isinstance(self.seed, type(None)):
            random.seed(self.seed)
            np.random.seed(self.seed)

        if isinstance(G, nx.classes.graph.Graph):
            self.G = G
        else:
            raise ValueError("G must be a NetworkX instance.")

        if isinstance(infection_rate, float) and 0.0 <= infection_rate <= 1.0:
            self.infection_rate = infection_rate
        else:
            raise ValueError("Infection rate must be a float between 0 and 1.")

        if not recovery_rate or (
            isinstance(recovery_rate, float) and 0.0 <= recovery_rate <= 1.0
        ):
            self.recovery_rate = recovery_rate
        else:
            raise ValueError("Recovery rate must be a float between 0 and 1.")

        if fraction_infected and number_infected:
            raise ValueError(
                "User can only provide one of fraction_infected, number_infected."
            )
        elif not fraction_infected and not number_infected:
            self.fraction_infected = fraction_infected
            self.number_infected = 1
        else:
            self.fraction_infected = fraction_infected
            self.number_infected = number_infected

        self._init_sim()
        self.history = []
        return None

    def _init_sim(self):
        """Initializes the diffusion process properties and initial infectivity."""        
        config = self.model_config # added by Zhiqian
        config.add_model_parameter("beta", self.infection_rate)

        if self.model == "sir":
            self.sim = ep.SIRModel(graph=self.G, seed=self.seed)
            if not self.recovery_rate:
                raise ValueError("Recovery rate must be defined for SIR model.")
            config.add_model_parameter("gamma", self.recovery_rate)
        elif self.model == "si":
            self.sim = ep.SIModel(graph=self.G, seed=self.seed)
        elif self.model == "sis":
            self.sim = ep.SISModel(graph=self.G, seed=self.seed)
            if not self.recovery_rate:
                raise ValueError("Recovery rate must be defined for SIS model.")
            config.add_model_parameter("lambda", self.recovery_rate)
        else:
            raise NotImplementedError("Diffusion model not recognized.")

        if self.number_infected:
            if not isinstance(self.seed, type(None)):
                random.seed(self.seed)
            infected = random.sample(range(len(self.G)), self.number_infected)
            config.add_model_initial_configuration("Infected", infected)
        elif self.fraction_infected:
            config.add_model_parameter("fraction_infected", self.fraction_infected)
        elif self.mc: # added by Zhiqian
            config = self.model_config
        else:
            raise NotImplementedError

        self.sim.set_initial_status(config)
        return None

    def forward(self, steps=100, verbose=False):
        """Executes specified number of diffusion process steps. Records simulation history.

        Parameters
        ----------
        steps : int
            Number of simulation steps.
        verbose : bool (default False)
            Specifies whether to return the simulation history.

        Notes
        -----
        Can be run more than once; this just adds steps to the simulation history.
        """
        self.history += self.sim.iteration_bunch(steps)
        if verbose:
            return self.history
        return None

    def reset_sim(self):
        """Resets the simulation to its initialized states. Does not preserve compartmental histories."""
        self.history = []
        self.sim.reset()
        return None

    def get_infected_indices(self, step=0):
        """Retrieves the indices of all vertices in the infected compartment at the provided step.

        Parameters
        ----------
        step : int
            Iteration step

        Returns
        -------
        list
        """
        nodes = list(self.G)

        def status_to_delta(status):
            """Converts the history's status to a vector representing movement in
            (+1) and out (-1) of the infected compartment

            Parameters
            ----------
            status : dict
                status dictionary from history, e.g. self.history[step]["status"]
            """
            delta = np.zeros(len(self.G))
            for idx in status:
                s = status[idx]
                if s == 1:
                    # node became infected this step
                    delta[idx] = 1
                if s == 2:
                    # node became removed this step
                    delta[idx] = -1
            return delta

        if step >= len(self.history):
            raise ValueError(
                "Invalid step. Continue the simulation to reach this step."
            )
        infected = np.zeros(len(self.G))
        for s in range(step + 1):
            infected += status_to_delta(self.history[s]["status"])
        return [nodes[i] for i in np.where(infected == 1)[0]]

    def get_infected_subgraph(self, step=0):
        """Returns the subgraph of the contact network whose vertices are marked infected.

        Parameters
        ----------
        step : int
            Iteration step

        Returns
        -------
        NetworkX Graph

        Notes
        -----
        This is only guaranteed to be connected in the SI model.
        """
        infected_indices = self.get_infected_indices(step=step)
        not_infected_indices = set(self.G.nodes) - set(infected_indices)
        H = self.G.copy()
        H.remove_nodes_from(not_infected_indices)
        return H

    def get_observers(self, observers=1):
        """Observers record the step number when they become infected. For a specified number
        or list of observers, returns a dict of observers and the timestamps at which they
        become infected.

        Parameters
        ----------
        observers : int or list
            If int, observers specifies the number of observation nodes
            If list, observers specifies the observation nodes directly

        Notes
        -----
        If self.model == "sis", nodes may be reinfected, so observers record a list of the timestamps
        at which they are infected. Otherwise, observers record one timestamp (step number) only.

        If an observer is not infected during the simulation history, its corresponding infection
        timestamp is recorded as infinity.
        """
        if not self.history:
            raise ValueError(
                "Simulation must be run before retrieving observer information."
            )
        timestamp_placeholder = np.inf if self.model == "si" else list()
        if isinstance(observers, int):
            if not isinstance(self.seed, type(None)):
                random.seed(self.seed)
                np.random.seed(self.seed)

            observer_dict = {
                i: timestamp_placeholder for i in random.sample(self.G.nodes, observers)
            }
        elif isinstance(observers, list):
            observer_dict = {i: timestamp_placeholder for i in observers}
        else:
            raise NotImplementedError

        for i in range(len(self.history)):
            status = self.history[i]["status"]
            if self.model == "sis":
                for j in observer_dict:
                    if j in status and status[j] == 1:
                        observer_dict[j].append(i)
            else:
                for j in observer_dict:
                    if j in status and status[j] == 1:
                        observer_dict[j] = i
        return observer_dict

    def get_source(self, return_subgraph=False):
        """Returns the vertices marked infected at initialization.

        Parameters
        ----------
        return_subgraph : bool
            If True, returns a subgraph of infected vertices.
            If False, returns a list of indices.

        Returns
        -------
        list or NetworkX Graph
        """
        if not isinstance(return_subgraph, bool):
            raise ValueError("return_subgraph param must be a bool")
        if return_subgraph:
            return self.get_infected_subgraph(step=0)
        return self.get_infected_indices(step=0)

    def get_frontier(self, step=0):
        """Retrieves the frontier set of a given step. This is the set of infected nodes
        with an uninfected neighbor.

        Parameters
        ----------
        step : int
            Iteration step

        Returns
        -------
        NetworkX Graph

        Notes
        -----
        In the SI model, the frontier set consists of nodes likely to have been
        infected last, by the given timestep.
        """
        T = self.get_infected_indices(step=step)
        S = [v for v in self.G if v not in T]
        frontier = nx.node_boundary(G=self.G, nbunch1=S, nbunch2=T)
        return frontier
    