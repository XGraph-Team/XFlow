import statistics as s
from IBM_baselines import IC, LT, SI

def blocking_effect_IC(g, config, seeds, selected_to_block):

    g_block = g.__class__()
    g_block.add_nodes_from(g)
    g_block.add_edges_from(g.edges)
    for a, b in g_block.edges():
        weight = config.config["edges"]['threshold'][(a, b)]
        g_block[a][b]['weight'] = weight

    for node in selected_to_block:
        g_block.remove_node(node)

    after = s.mean(IC(g_block, config, seeds))

    before = s.mean(IC(g, config, seeds))

    return before - after

def blocking_effect_SI(g, config, seeds, selected_to_block, beta=0.1):

    g_block = g.__class__()
    g_block.add_nodes_from(g)
    g_block.add_edges_from(g.edges)
    for a, b in g_block.edges():
        weight = config.config["edges"]['threshold'][(a, b)]
        g_block[a][b]['weight'] = weight

    for node in selected_to_block:
        g_block.remove_node(node)

    after = s.mean(SI(g_block, config, seeds, beta=beta))

    before = s.mean(SI(g, config, seeds, beta=beta))

    return before - after