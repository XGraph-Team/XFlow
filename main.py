from xflow.dataset import connSW, Cora, BA
from xflow.seed import random as seed_random
from xflow.diffusion import IC, SI
from xflow.seed import random as seed_random, degree as seed_degree, eigen as seed_eigen

# graphs to test
fn = lambda: connSW(n=1000, beta=0.1)
fn.__name__ = 'connSW'
gs = [Cora, fn, BA]

# diffusion models to test
# TODO actually, no need to import in this main.py, because the diffusion models are embeded in the methods
df = [SI, IC]

# seed configurations to test
# TODO
se = [seed_random, seed_degree, seed_eigen]

def run (graph, diffusion, seed, method, eval, epoch, output):
    print(eval)

    for graph_fn in graph:
        try:
            print(graph_fn.__name__)
            g, config = graph_fn()
            print(g)
            # print(config)

            for method_fn in method:
                try:
                    print(method_fn.__name__)
                    if method_fn.__name__ == 'pi':
                        m = method_fn(g, config, budget=10)
                    if method_fn.__name__ == 'celfpp':
                        for diffusion_fn in diffusion:
                            try:
                                print(diffusion_fn.__name__)
                                m = method_fn(g, config, budget=10, rounds=epoch, model=diffusion_fn.__name__, beta=0.1)
                            except Exception as e:
                                print(f"Error when calling {diffusion_fn.__name__}: {str(e)}")
                        
                    
                except Exception as e:
                    print(f"Error when calling {method_fn.__name__}: {str(e)}")    

        except Exception as e:
            print(f"Error when calling {graph_fn.__name__}: {str(e)}")


# configurations of IM experiments
from xflow.method.im import pi as im_pi, degree as im_degree, sigma as im_sigma, celfpp as im_celfpp
me = [im_pi]
rt = run (
    graph = gs, diffusion = df, seed = se,
    method = me, eval = 'im', epoch = 10,
    output = [ 'animation', 'csv', 'fig'])

# configurations of IBM experiments
from xflow.method.ibm import pi as ibm_pi, degree as ibm_degree, sigma as ibm_sigma, greedySI as ibm_greedySI
me = [ibm_pi, ibm_greedySI]
rt = run (
    graph = gs, diffusion = df, seed = se,
    method = me, eval = 'ibm', epoch = 10,
    output = [ 'animation', 'csv', 'fig'])
