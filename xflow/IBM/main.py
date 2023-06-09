from graph_generation import *
from IBM_baselines import *
from evaluation import *

print('exp 1')

g, config = connSW(1000, 0.1)
print('connSW is on.')

seeds = random.sample(list(g.nodes()), 10)

print('seeds: ', seeds)

beta = 0.1

for budget in [5, 10, 15, 20, 25, 30]:

    print('budget: ', budget)

    # greedy
    selected = greedySI(g, config, budget, seeds, beta=beta)
    print('greedy: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # eigen
    selected = eigen(g, config, budget)
    print('eigen: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # degree
    selected = degree(g, config, budget)
    print('degree: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # sigma
    selected = sigma(g, config, budget)
    print('sigma: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # pi
    selected = pi(g, config, budget)
    print('pi: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

####################################################################################################

print('exp 2')

g, config = connSW(1000, 0.1)
print('connSW is on.')

seeds = random.sample(list(g.nodes()), 10)

print('seeds: ', seeds)

for beta in [0.1,0.2,0.3,0.4,0.5]:
    print('beta: ', beta)

    # greedy
    selected = greedySI(g, config, budget, seeds, beta=beta)
    print('greedy: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # eigen
    selected = eigen(g, config, budget)
    print('eigen: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # degree
    selected = degree(g, config, budget)
    print('degree: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # sigma
    selected = sigma(g, config, budget)
    print('sigma: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # pi
    selected = pi(g, config, budget)
    print('pi: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)


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
    selected = greedySI(g, config, budget, seeds, beta=beta)
    print('greedy: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # eigen
    selected = eigen(g, config, budget)
    print('eigen: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # degree
    selected = degree(g, config, budget)
    print('degree: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # sigma
    selected = sigma(g, config, budget)
    print('sigma: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

    # pi
    selected = pi(g, config, budget)
    print('pi: ', selected)
    effect = blocking_effect_SI(g, config, seeds, selected, beta=beta)
    print('blocked: ', effect)

