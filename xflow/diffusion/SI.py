import torch_geometric.datasets as ds
import random
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc


def SI(g, config, seed, rounds=100, beta=0.1):

    result = []

    for iter in range(rounds):

        model_temp = ep.SIModel(g) # _temp
        config_temp = mc.Configuration()
        config_temp.add_model_initial_configuration('Infected', seed)
        config_temp.add_model_parameter('beta', beta)

        for a, b in g.edges(): # _temp
            weight = config.config["edges"]['threshold'][(a, b)]
            config_temp.add_edge_configuration('threshold', (a, b), weight)

        model_temp.set_initial_status(config_temp)

        iterations = model_temp.iteration_bunch(5)

        result.append(iterations[4]['node_count'][1])

    return result
