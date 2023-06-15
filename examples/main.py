import sys
import os
current_script_directory = os.path.dirname(os.path.abspath(__file__))
xflow_path = os.path.join(current_script_directory, '..', '..', 'xflow')
sys.path.insert(1, xflow_path)

from xflow.dataset.nx import BA, connSW
from xflow.dataset.pyg import Cora
from xflow.diffusion.SI import SI
from xflow.diffusion.IC import IC
from xflow.diffusion.LT import LT
from xflow.seed import random as seed_random, degree as seed_degree, eigen as seed_eigen
import random

# graphs to test
fn = lambda: connSW(n=1000, beta=0.1)
fn.__name__ = 'connSW'
gs = [Cora, fn, BA]

# diffusion models to test
# TODO actually, no need to import in this main.py, because the diffusion models are embeded in the methods
df = [SI, IC, LT]

# seed configurations to test
# TODO seeds are embeded in the methods too
se = [seed_random, seed_degree, seed_eigen]

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


# configurations of IM experiments
from xflow.method.im import pi as im_pi, degree as im_degree, sigma as im_sigma, celfpp as im_celfpp, greedy as im_greedy
me = [im_pi]
rt = run (
    graph = gs, diffusion = df, seeds = se,
    method = me, eval = 'im', epoch = 10, 
    budget = 10, 
    output = [ 'animation', 'csv', 'fig'])

# # configurations of IBM experiments
# from xflow.method.ibm import pi as ibm_pi, degree as ibm_degree, sigma as ibm_sigma, greedy as ibm_greedy
# me = [ibm_pi, ibm_greedy]
# rt = run (
#     graph = gs, diffusion = df, seeds = se,
#     method = me, eval = 'ibm', epoch = 10,
#     budget = 10,
#     output = [ 'animation', 'csv', 'fig'])

# # configurations of SL experiments
# rt = run (
#     graph = gs, diffusion = df, seeds = se,
#     method = me, eval = 'sl', epoch = 10,
#     budget = 10,
#     output = [ 'animation', 'csv', 'fig'])
