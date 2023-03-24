import ndlib
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
import pandas as pd
from util import combinations, subcombs, substract
import random

def simulationIC(r, g, result, config):

    title = []
    for i in result:
        title.append(i)
    title.append('result')

    df = pd.DataFrame(columns=title)

    n = len(result)

    for combs in combinations(result):
        input = []
        for i in range(n):
            item = 1 if result[i] in combs else 0
            input.append(item)

        for i in range(r):

            input1 = []
            for item in input:
                input1.append(item)

            g_mid = g.__class__()
            g_mid.add_nodes_from(g)
            g_mid.add_edges_from(g.edges)

            model_mid = ep.IndependentCascadesModel(g_mid)
            config_mid = mc.Configuration()
            config_mid.add_model_initial_configuration('Infected', combs)

            for a, b in g_mid.edges():
                weight = config.config["edges"]['threshold'][(a, b)]
                g_mid[a][b]['weight'] = weight
                config_mid.add_edge_configuration('threshold', (a, b), weight)

            model_mid.set_initial_status(config_mid)

            iterations = model_mid.iteration_bunch(5)
            trends = model_mid.build_trends(iterations)

            total_no = 0

            for j in range(5):
                a = iterations[j]['node_count'][1]
                total_no += a

            input1.append(total_no)

#            newdf = pd.DataFrame([[zero, one, two, three, four, total_no]], columns = title)
            newdf = pd.DataFrame([input1], columns=title)

#            df = df.append({title[0]: zero, title[1]: one, title[2]: two, title[3]: three, title[4]: four, title[5]: total_no},ignore_index=True)
            df = pd.concat([df,newdf])
    return df

def simulationLT(r, g, result, config):

    title = []
    for i in result:
        title.append(i)
    title.append('result')

    df = pd.DataFrame(columns=title)

    n = len(result)

    for combs in combinations(result):
        input = []
        for i in range(n):
            item = 1 if result[i] in combs else 0
            input.append(item)

        for i in range(r):

            input1 = []
            for item in input:
                input1.append(item)

            g_mid = g.__class__()
            g_mid.add_nodes_from(g)
            g_mid.add_edges_from(g.edges)

            model_mid = ep.ThresholdModel(g_mid)
            config_mid = mc.Configuration()
            config_mid.add_model_initial_configuration('Infected', combs)

            for a, b in g_mid.edges():
                weight = config.config["edges"]['threshold'][(a, b)]
                g_mid[a][b]['weight'] = weight
                config_mid.add_edge_configuration('threshold', (a, b), weight)

            for i in g_mid.nodes():
                threshold = random.randrange(1, 20)
                threshold = round(threshold / 100, 2)
                config_mid.add_node_configuration("threshold", i, threshold)

            model_mid.set_initial_status(config_mid)

            iterations = model_mid.iteration_bunch(5)
            trends = model_mid.build_trends(iterations)

            total_no = iterations[4]['node_count'][1]
            input1.append(total_no)

            newdf = pd.DataFrame([input1], columns=title)

            df = pd.concat([df,newdf])
    return df
