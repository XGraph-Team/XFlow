import torch_geometric.datasets as ds
import random
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc


# diffusion models
def IC(g, config, seed, rounds=100):
    result = []

    for iter in range(rounds):

        model_temp = ep.IndependentCascadesModel(g) # _temp
        config_temp = mc.Configuration()
        config_temp.add_model_initial_configuration('Infected', seed)

        for a, b in g.edges(): # _temp
            weight = config.config["edges"]['threshold'][(a, b)]
            # g_temp[a][b]['weight'] = weight
            config_temp.add_edge_configuration('threshold', (a, b), weight)

        model_temp.set_initial_status(config_temp)

        iterations = model_temp.iteration_bunch(5)

        total_no = 0

        for j in range(5):
            a = iterations[j]['node_count'][1]
            total_no += a

        result.append(total_no)

    return result

def LT(g, config, seed, rounds=100):
    result = []

    for iter in range(rounds):

        model_temp = ep.ThresholdModel(g) # _temp
        config_temp = mc.Configuration()
        config_temp.add_model_initial_configuration('Infected', seed)

        for a, b in g.edges(): # _temp
            weight = config.config["edges"]['threshold'][(a, b)]
            # g_temp[a][b]['weight'] = weight
            config_temp.add_edge_configuration('threshold', (a, b), weight)

        for i in g.nodes():
            threshold = random.randrange(1, 20)
            threshold = round(threshold / 100, 2)
            config_temp.add_node_configuration("threshold", i, threshold)

        model_temp.set_initial_status(config_temp)

        iterations = model_temp.iteration_bunch(5)

        total_no = iterations[4]['node_count'][1]

        result.append(total_no)

    return result

# Zonghan's code
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
