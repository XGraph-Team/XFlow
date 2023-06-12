from xflow.dataset import Cora , random , BA
from xflow.diffusion import IC , SI
# from xflow.seed import random , degree , eigen
from xflow.method.im import celf , sigma
# graphs to test
gs = [ cora , random , ba ]
# diffusion models to test
df = [ic , si ]
# seed configurations to test
se = [ random , degree , eigen ]
# methods to test
me = [ celf , sigma , imrank ]
# configurations of experiments
rt = run ( graph =gs , diffusion = df , seed =se,
method =me , eval = 'im', epoch =10 ,
output =[ 'animation', 'csv', 'fig'])