import xflow_loader

from xflow.dataset.nx import BA, connSW
from xflow.dataset.pyg import Cora
from xflow.diffusion import SI, IC, LT
from xflow.seed import random as seed_random, degree as seed_degree, eigen as seed_eigen
from xflow.util import run

# graphs to test
fn = lambda: connSW(n=1000, beta=0.1)
fn.__name__ = 'connSW'
gs = [fn, BA]

# diffusion models to test
# TODO actually, no need to import in this main.py, because the diffusion models are embeded in the methods
df = [SI, IC, LT]

# configurations of IM experiments
from xflow.method.im import pi as im_pi, degree as im_degree, sigma as im_sigma, eigen as im_eigen, celf as im_celf,celfpp as im_celfpp, greedy as im_greedy
me = [im_pi, im_eigen]
rt = run (
    graph = gs, diffusion = df, 
    method = me, eval = 'im', epoch = 10, 
    budget = 10, 
    output = [ 'animation', 'csv', 'fig'],
    seeds = seed_random)

# configurations of IBM experiments
from xflow.method.ibm import pi as ibm_pi, degree as ibm_degree, sigma as ibm_sigma, eigen as im_eigen, greedy as ibm_greedy
me = [ibm_pi, ibm_sigma, ibm_degree]
rt = run (
    graph = gs, diffusion = df, 
    method = me, eval = 'ibm', epoch = 10,
    budget = 10,
    output = [ 'animation', 'csv', 'fig'],
    seeds = seed_random)
 
# configurations of SL experiments
from xflow.method.cosasi.source_inference.multiple_source.netsleuth import netsleuth, fast_multisource_netsleuth
from xflow.method.cosasi.source_inference.multiple_source.lisn import fast_multisource_lisn
from xflow.method.cosasi.source_inference.multiple_source.jordan import fast_multisource_jordan_centrality

me = [netsleuth]
rt = run (
    graph = gs, diffusion = df, 
    method = me, eval = 'sl', epoch = 10,
    budget = 10,
    output = [ 'animation', 'csv', 'fig'],
    seeds = seed_random)
