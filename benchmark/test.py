import networkx as nx
from time import time

from graphGeneration import Cora, CiteSeer, PubMed, connSW, ER, coms, photo
from baselines import pi, eigen, degree, celfpp, celf, greedy,IMRank,RIS
from score import effectIC

g, config = Cora()

print("Cora graph is on.")
# print(nx.info(g))

# print('------------------------------------------------')
# print('pi')
# start = time()
# set = pi(g,config,5)
# end = time()
# print("time: ", end-start)
# ie,var = effectIC(g, config, set)
# print('IE:', ie, " +_ ", var)

# print('------------------------------------------------')
# print('Simulation eigen')
# start = time()
# set = eigen(g,config,5)
# end = time()
# print("time: ", end-start)
# ie,var = effectIC(g, config, set)
# print('IE:', ie, " +_ ", var)

# print('Simulation IMrank')
# start = time()
# set = IMRank(g,config,5)
# end = time()
# print("time: ", end-start)
# ie,var = effectIC(g, config, set)
# print('IE:', ie, " +_ ", var)

print('Simulation RIS')
start = time()
set = RIS(g,config,5)
end = time()
print("time: ", end-start)
ie,var = effectIC(g, config, set)
print('IE:', ie, " +_ ", var)

# print('Simulation CELF++')
# start = time()
# set = celfpp(g,config,5)
# end = time()
# print("time: ", end-start)
# ie,var = effectIC(g, config, set)
# print('IE:', ie, " +_ ", var)

# print('Simulation CELF++ 2')
# start = time()
# set = celfpp2(g,config,5)
# end = time()
# print("time: ", end-start)

print('Simulation CELF')
start = time()
set = celf(g,config,5)
end = time()
print("time: ", end-start)
ie,var = effectIC(g, config, set)
print('IE:', ie, " +_ ", var)

# print('Simulation CELF 2')
# start = time()
# set = celf2(g,config,5)
# end = time()
# print("time: ", end-start)

print('Simulation greedy')
start = time()
set = greedy(g,config,5)
end = time()
print("time: ", end-start)
ie,var = effectIC(g, config, set)
print('IE:', ie, " +_ ", var)
