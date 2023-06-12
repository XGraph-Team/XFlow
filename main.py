from xflow.dataset import Cora, random, BA
from xflow.diffusion import IC, SI
from xflow.seed import random, degree, eigen
from xflow.method.im import pi, degree, sigma

def run ( graph, diffusion, seed, method, eval, epoch, output):
    print ('Run')

# graphs to test
gs = [ Cora , random , BA ]

# diffusion models to test
df = [IC , SI ]

# seed configurations to test
se = [random, degree, eigen]

# methods to test
me = [pi, degree, sigma]

# configurations of experiments
rt = run (
    graph = gs, diffusion = df, seed = se,
    method = me, eval = 'im', epoch = 10,
    output = [ 'animation', 'csv', 'fig'])