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
from xflow.util import run

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
