# from xflow.dataset import connSW, Cora, random as dataset_random, BA
from xflow.dataset import rand as dataset_random, Cora, BA
# from xflow.seed import random as seed_random
from xflow.seed import random as seed_random
from xflow.diffusion import IC, SI
from xflow.seed import random as seed_random, degree as seed_degree, eigen as seed_eigen
from xflow.method.im import pi, degree as im_degree, sigma as im_sigma

# graphs to test
gs = [Cora, lambda: dataset_random(1000, 0.001, 10), BA]

# diffusion models to test
df = [IC, SI]

# seed configurations to test
se = [seed_random, seed_degree, seed_eigen]

# methods to test
me = [pi, im_degree, im_sigma]

def run (graph, diffusion, seed, method, eval, epoch, output):

    for graph_fn in graph: # renaming `graph` to `graph_fn` to avoid naming conflicts
        try:
            print('graph')
            g, config = graph_fn()  # Calls the function directly
            print(g)
            print(config)
        except Exception as e:
            print(f"Error when calling {graph_fn.__name__}: {str(e)}")

    for diffusion_fn in diffusion: # renaming `graph` to `graph_fn` to avoid naming conflicts
        try:
           print('diffusion')
        except Exception as e:
            print(f"Error when calling {diffusion_fn.__name__}: {str(e)}")

# configurations of experiments
rt = run (
    graph = gs, diffusion = df, seed = se,
    method = me, eval = 'im', epoch = 10,
    output = [ 'animation', 'csv', 'fig'])