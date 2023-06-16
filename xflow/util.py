import random

def run (graph, diffusion, seeds, method, eval, epoch, budget, output):
    print("Running " + eval.upper() + " :")

    for graph_fn in graph:
        try:
            print(graph_fn.__name__)
            g, config = graph_fn()
            print(g)
            seeds = random.sample(list(g.nodes()), 10)

            for method_fn in method:
                try:
                    print(method_fn.__name__)
                    baselines = ['eigen', 'degree', 'pi', 'sigma', 'Netshield', 'IMRank']
                    if method_fn.__name__ in baselines:
                        m = method_fn(g, config, budget=10)
                    baselines = ['RIS']
                    if method_fn.__name__ in baselines:
                        m = method_fn(g, config, budget=10)
                    baselines = ['greedy', 'celf', 'celfpp']
                    if method_fn.__name__ in baselines:
                        for diffusion_fn in diffusion:
                            try:
                                print(diffusion_fn.__name__)
                                if eval == 'im':
                                    m = method_fn(g, config, budget, rounds=epoch, model=diffusion_fn.__name__, beta=0.1)
                                if eval == 'ibm':
                                    m = method_fn(g, config, budget, seeds, rounds=epoch, model=diffusion_fn.__name__, beta=0.1)
                            except Exception as e:
                                print(f"Error when calling {diffusion_fn.__name__}: {str(e)}")
                        
                    
                except Exception as e:
                    print(f"Error when calling {method_fn.__name__}: {str(e)}")    

        except Exception as e:
            print(f"Error when calling {graph_fn.__name__}: {str(e)}")