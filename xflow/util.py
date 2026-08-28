import random

import numpy as np

import xflow.method.cosasi as co
import xflow.method.im as im_methods


# Seed sets are no longer configured separately: they are produced by the IM
# methods in ``xflow.method.im`` (the former ``xflow.seed`` module is gone).
# ``seed_method`` below is any of those methods, e.g. ``im_methods.random``,
# ``im_methods.degree`` or ``im_methods.eigen``.
def run(graph, diffusion, method, eval, epoch, budget, output,
        seed_method=im_methods.random, seed_budget=None, seed=None):

    print("Running " + eval.upper() + " :")

    if seed_budget is None:
        seed_budget = budget

    results = {}

    for graph_fn in graph:
        try:
            print(graph_fn.__name__)
            g, config = graph_fn()
            print(g)

            # seeds come from an IM method instead of a dedicated seed module
            seeds = None
            if eval == 'ibm':
                print('seeds by ' + seed_method.__name__)
                seeds = seed_method(g, config, seed_budget)

            for method_fn in method:
                try:
                    print(method_fn.__name__)
                    sims = None
                    baselines = ['random', 'eigen', 'degree', 'pi', 'sigma', 'Netshield', 'IMRank']
                    if method_fn.__name__ in baselines:
                        sims = method_fn(g, config, budget)
                    baselines = ['RIS']
                    if method_fn.__name__ in baselines:
                        sims = method_fn(g, config, budget, rounds=epoch)
                    baselines = ['greedy', 'celf', 'celfpp']
                    if method_fn.__name__ in baselines:
                        for diffusion_fn in diffusion:
                            try:
                                print(diffusion_fn.__name__)
                                if eval == 'im':
                                    sims = method_fn(g, config, budget, rounds=epoch, model=diffusion_fn.__name__, beta=0.1)
                                if eval == 'ibm':
                                    sims = method_fn(g, config, budget, seeds, rounds=epoch, model=diffusion_fn.__name__, beta=0.1)
                            except Exception as e:
                                print(f"Error when calling {diffusion_fn.__name__}: {str(e)}")

                    if method_fn.__name__ == 'netsleuth':
                        # ``seed`` here is the random number generation state,
                        # not a seed set of nodes
                        if seed is not None:
                            random.seed(seed)
                            np.random.seed(seed)

                        contagion = co.StaticNetworkContagion(
                            G=g,
                            model="si",
                            infection_rate=0.1,
                            # recovery_rate=0.005, # for SIS/SIR models
                            number_infected = 2,
                            seed=seed
                        )

                        contagion.forward(steps = 16)
                        
                        step = 15

                        # This obtains the indices of all vertices in the infected category at the 15th step of the simulation.
                        I = contagion.get_infected_subgraph(step=step)
                        print(I)
                        sims = method_fn(I=I, G=g, hypotheses_per_step=1)
                        true_source = contagion.get_source()
                        evals = sims.evaluate(true_source)
                        top_dis= evals["distance"]["top score's distance"]
                        print(top_dis)

                    results[(graph_fn.__name__, method_fn.__name__)] = sims

                except Exception as e:
                    print(f"Error when calling {method_fn.__name__}: {str(e)}")    

        except Exception as e:
            print(f"Error when calling {graph_fn.__name__}: {str(e)}")

    return results
