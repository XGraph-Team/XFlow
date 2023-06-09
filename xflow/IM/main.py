import networkx as nx
from time import time

from graph_generation import Cora, CiteSeer, PubMed, connSW, ER, coms, photo
from IM_baselines import eigen, degree, pi, sigma, greedy, celf, celfpp, IMRank, RIS, IMM
from evaluation import effectSI

def analyze(seed, beta, size):
    g, config = connSW(size, beta)
    print('beta', beta)
    print('seed', seed)
    print('size', size)

    # print('------------------------------------------------')
    # print('pi')
    # start = time()
    # set = pi(g,config,seed)
    # end = time()
    # print("time: ", end-start)
    # ie,var = effectSI(g, config, set, beta)
    # print('IE:', ie, " +_ ", var)

    # print('------------------------------------------------')
    # print('degree')
    # start = time()
    # set = degree(g,config,seed)
    # end = time()
    # print('time: ', end - start)
    # ie,var = effectSI(g, config, set, beta)
    # print('IE:', ie, " +_ ", var)

    # print('------------------------------------------------')
    # print('eigen-centrality')
    # start = time()
    # set = eigen(g, config, seed)
    # end = time()
    # print('time: ', end - start)
    # ie,var = effectSI(g, config, set, beta)
    # print('IE:', ie, " +_ ", var)

    
#     print('------------------------------------------------')
#     print('RIS')
#     start = time()
#     set = RIS(g, config, seed)
#     end = time()
#     print('time: ', end - start)
#     ie,var = effectSI(g, config, set, beta)
#     print('IE:', ie, " +_ ", var)

    print('------------------------------------------------')
    print('celfpp')
    start = time()
    set = celfpp(g,config,seed, rounds=100, model='SI', beta=beta)
    end = time()
    print('time: ', end - start)
    ie,var = effectSI(g, config, set, beta)
    print('IE:', ie, " +_ ", var)

    # print('------------------------------------------------')
    # print('IMRank')
    # start = time()
    # set = IMRank(g,config,seed)
    # end = time()
    # print('time: ', end - start)
    # ie,var = effectSI(g, config, set, beta)
    # print('IE:', ie, " +_ ", var)

    print('------------------------------------------------')
    print('IMM')
    start = time()
    set = IMM(g, config, seed, rounds=100, model='SI', beta=beta)
    end = time()
    print('time: ', end - start)
    ie,var = effectSI(g, config, set, beta)
    print('IE:', ie, " +_ ", var)


# for chart 1
# print("seed = [5, 10, 15, 20, 25, 30];  beta = 0.1; size = 1000")
# analyze(5, 0.1, 1000)
# analyze(10, 0.1, 1000)
# analyze(15, 0.1, 1000)
# analyze(20, 0.1, 1000)
# analyze(25, 0.1, 1000)
# analyze(30, 0.1, 1000)

# for chart 2
print("seed = 5; beta = [0.1, 0.2, 0.3, 0.4, 0.5]; size = 1000")
analyze(5, 0.1, 1000)
analyze(5, 0.2, 1000)
analyze(5, 0.3, 1000)
analyze(5, 0.4, 1000)
analyze(5, 0.5, 1000)

# # for chart 3
# print("seed = 5; beta = 0.1; size = [200, 400, 600, 800, 1000]")
# analyze(5, 0.1, 200)
# analyze(5, 0.1, 400)
# analyze(5, 0.1, 600)
# analyze(5, 0.1, 800)
# analyze(5, 0.1, 1000)
