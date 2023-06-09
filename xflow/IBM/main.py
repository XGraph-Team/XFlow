from graph_generation import *
from IBM_baselines import *
from evaluation import *
import time

print('exp 1')

g, config = connSW(1000, 0.1)
print('connSW is on.')

seeds = random.sample(list(g.nodes()), 10)

print('seeds: ', seeds)

beta = 0.1

for budget in [5, 10, 15, 20, 25, 30]:

    print('budget: ', budget)

    # greedy
    start = time.time()
    selected = greedySI(g, config, budget, seeds, beta=beta)
    end = time.time()
    print('time: ', end - start)
    print('greedy: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

    # eigen
    start = time.time()
    selected = eigen(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('eigen: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

    # degree
    start = time.time()
    selected = degree(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('degree: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

    # sigma
    start = time.time()
    selected = sigma(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('sigma: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

    # pi
    start = time.time()
    selected = pi(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('pi: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

####################################################################################################

print('exp 2')

g, config = connSW(1000, 0.1)
print('connSW is on.')

seeds = random.sample(list(g.nodes()), 10)

print('seeds: ', seeds)

for beta in [0.1,0.2,0.3,0.4,0.5]:
    print('beta: ', beta)

    # greedy
    start = time.time()
    selected = greedySI(g, config, budget, seeds, beta=beta)
    end = time.time()
    print('time: ', end - start)
    print('greedy: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)
    # eigen
    start = time.time()
    selected = eigen(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('eigen: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

    # degree
    start = time.time()
    selected = degree(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('degree: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

    # sigma
    start = time.time()
    selected = sigma(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('sigma: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

    # pi
    start = time.time()
    selected = pi(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('pi: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)


####################################################################################################

print('exp 3')

for n in [200,400,600,800,1000]:

    g, config = connSW(n, 0.1)

    print('connSW is on.')
    print('n: ', n)

    seeds = random.sample(list(g.nodes()), 10)

    print('seeds: ', seeds)

    budget = 5
    beta = 0.1

    # greedy
    start = time.time()
    selected = greedySI(g, config, budget, seeds, beta=beta)
    end = time.time()
    print('time: ', end - start)
    print('greedy: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

    # eigen
    start = time.time()
    selected = eigen(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('eigen: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

    # degree
    start = time.time()
    selected = degree(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('degree: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

    # sigma
    start = time.time()
    selected = sigma(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('sigma: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)

    # pi
    start = time.time()
    selected = pi(g, config, budget)
    end = time.time()
    print('time: ', end - start)
    print('pi: ', selected)
    mean, std = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', mean, '+-', std)
