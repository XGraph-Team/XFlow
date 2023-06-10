import networkx as nx
import cosasi
import random
import numpy as np
from graph_generation import CiteSeer, PubMed, Cora, coms, photo, connSW, rand
from time import time
import tracemalloc
import logging
# from memory_profiler import profile

tracemalloc.start()

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a file handler
file_handler = logging.FileHandler('output.log')
file_handler.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Now, logging.info() etc. will write to both the file and the console:
# logger.info("This is an info message.")

def get_result(sims, true_source):
#     start = time()
    
    # Rank nodes by score
#     logger.info('Rank : %s', sims.rank())

    # Returns the top n item indices by rank
#     logger.info('Top n item : %s', sims.topn(n=5))
   
    # Finds the rank of the true source, by the algorithm's scoring protocol.
#     logger.info('Evaluate solution rank : %s', sims.evaluate_solution_rank(true_source))
   
    # Finds the shortest path length between each node in the solution set and the true souce.
#     logger.info('Shortest Distance : %s', sims.evaluate_distance(true_source))

    # Runs evaluation algorithms and returns a dictionary of results
    evals = sims.evaluate(true_source)

    # logger.info('evals', evals)

    # solution rank
    # Where feasible, cosasi enhances localization algorithms to execute ranking across multiple hypotheses. This approach enables us to rank all hypotheses based on the algorithm's inherent scoring criteria and provide the rank of the actual source amongst all hypotheses. This resembles the commonly used "precision at k" metric in the field of information retrieval.
    #Therefore, according to this algorithm, the real source was the nth most probable hypothesis.
#     logger.info('solution rank of nth : %s', evals["rank"])

    # rank / len(self.data["scores"])
#     print('evals rank % :', evals["rank %"])

    #  a metric that assesses the minimum graph distance between vertex sets that may be of different sizes
    # The top-scoring hypothesis was close to the true source.
    top_dis= evals["distance"]["top score's distance"]
    logger.info('top score distance : %s', top_dis)

    # evaluate the distance from true source of all computed hypotheses
#     distances = evals["distance"]["all distances"].values()
    # logger.info('all distances', distances)

    # the distance from true source of these hypotheses ranged from min to max
#     logger.info('min distances : %s',min(distances))
#     logger.info('max distances : %s',max(distances))
    
    # todo: add more metrics
    
#     end = time()
#     logger.info('time : %s', end - start)


# @profile
def analyze_graph(G, seed):

    # record memory usage
#     snapshot = tracemalloc.take_snapshot()
#     top_stats = snapshot.statistics('lineno')
#     for stat in top_stats[:10]:
#         logger.info(stat)

    random.seed(seed)
    np.random.seed(seed)

    contagion = cosasi.StaticNetworkContagion(
        G=G,
        model="si",
        infection_rate=0.1,
        # recovery_rate=0.005, # for SIS/SIR models
        number_infected = 3,
        seed=seed
    )

    contagion.forward(steps = 16)
    
    step = 15

    # This obtains the indices of all vertices in the infected category at the 15th step of the simulation.
    I = contagion.get_infected_subgraph(step=step)
    logger.info('Infected Subgraph : %s',I)

    # #benchmark
    # benchmark = cosasi.BenchmarkFromSimulation(
    #     contagion=contagion,
    #     information_type="single snapshot",
    #     t=step
    # )
    # logger.info('benchmark for sims : %s', benchmark)
    # results = benchmark.go()
    # logger.info('benchmark result for sims : %s',results)

    # benchmark = cosasi.BenchmarkFromDetails(
    #     true_source=true_source,
    #     G=G,
    #     I=I,
    #     t=step,
    #     number_sources=len(true_source),
    #     information_type="single snapshot"
    # )
    # logger.info('benchmark : %s', benchmark)

    # results = benchmark.go()
    # logger.info('benchmark result : %s', results)

    # estimate the number of sources
#     number_sources = cosasi.utils.estimators.number_sources(I=I, number_sources=None, return_source_subgraphs=False, number_sources_method="eigengap")
#     logger.info('estimated number of sources : %s', number_sources)

    # alternative estimate the number of sources
#     alt_number_sources = cosasi.utils.estimators.number_sources(I=I, number_sources=None, return_source_subgraphs=False, number_sources_method="netsleuth", G=G)
#     logger.info('alternative estimated number of sources : %s', alt_number_sources)

    # estimate the number of sources and return the source subgraphs
#     opt_number_sources, subgraphs = cosasi.utils.estimators.number_sources(I=I, number_sources=None, return_source_subgraphs=True)
#     logger.info('optional estimated number of sources : %s', opt_number_sources)
    # logger.info('subgraphs', subgraphs)

    # The most frequently encountered data type in literature concerning source inference is known as a "snapshot." This refers to a comprehensive set of infection data provided for a specific point in time.    
    # infected_indices = contagion.get_infected_indices(step=step)
    # logger.info('Infected indices', infected_indices)

    # On the other hand, certain algorithms utilize "observers," a select group of vertices designated to keep track of their infection status. In cosasi's implementation, the user determines the number of these observers, and their specific selection is carried out in a uniformly random manner.
    # observers = contagion.get_observers(observers=5)
    # logger.info('Observers', observers)

    # Some algorithms make use of an analytical concept known as the infection frontier, which represents the collection of infected vertices that have infected neighbors. This concept is particularly relevant to the Susceptible-Infected (SI) epidemic model, where vertices do not recover from the infection. Under these circumstances, the frontier set is comprised of nodes that could have been the most recently infected by the given point in time.
    # frontier = contagion.get_frontier(step=step)
    # logger.info('Frontier',frontier)

    # Objects of the StaticNetworkContagion class store their compartmental histories. These histories can be accessed through their 'history' attribute.
    # logger.info('history', contagion.history)

    true_source = contagion.get_source()
    logger.info('True Source : %s',true_source)

    # implementation of NETSLEUTH providing no information about the number of sources
    start = time()
    logger.info('multisource netsleuth hypotheses_per_step=1')
    sims = cosasi.source_inference.multiple_source.netsleuth(I=I, G=G, hypotheses_per_step=1)
    get_result(sims, true_source)
    end = time()
    logger.info('time : %s', end - start)
    
#     logger.info('multisource netsleuth hypotheses_per_step=2')
#     sims = cosasi.source_inference.multiple_source.netsleuth(I=I, G=G, hypotheses_per_step=2)
#     get_result(sims, true_source)
    
#     logger.info('multisource netsleuth hypotheses_per_step=3')
#     sims = cosasi.source_inference.multiple_source.netsleuth(I=I, G=G, hypotheses_per_step=3)
#     get_result(sims, true_source)

    # implementation of LISN providing no information about the number of sources
#     logger.info('fast multisource lisn')
#     sims = cosasi.source_inference.multiple_source.fast_multisource_lisn(I=I, G=G, t=step)
#     get_result(sims, true_source)

    # unofficial implementation of NETSLEUTH providing no information about the number of sources
#     logger.info('fast multisource netsleuth')
#     sims = cosasi.multiple_source.fast_multisource_netsleuth(I=I, G=G)
#     get_result(sims, true_source)

    # implementation of jordan centrality providing no information about the number of sources
#     logger.info('fast multisource jordan centrality')
#     sims = cosasi.multiple_source.fast_multisource_jordan_centrality(I=I, G=G)
#     get_result(sims, true_source)

    ###############################
    
    # unofficial implementation of NETSLEUTH assuming 2 sources
    start = time()
    logger.info('fast multisource netsleuth assuming 2 sources')
    sims = cosasi.source_inference.multiple_source.fast_multisource_netsleuth(I=I, G=G, number_sources=2)
    get_result(sims, true_source)
    end = time()
    logger.info('time : %s', end - start)
    
    # implementation of jordan centrality assuming 2 sources
    start = time()
    logger.info('fast multisource jordan centrality assuming 2 sources')
    sims = cosasi.source_inference.multiple_source.fast_multisource_jordan_centrality(I=I, G=G, number_sources=2)
    get_result(sims, true_source)
    end = time()
    logger.info('time : %s', end - start)

    # implementation of LISN assuming 3 sources
    start = time()
    logger.info('fast multisource lisn assuming 2 sources')
    sims = cosasi.source_inference.multiple_source.fast_multisource_lisn(I=I, G=G, t=step, number_sources=2)
    get_result(sims, true_source)
    end = time()
    logger.info('time : %s', end - start)

    contagion.reset_sim()

for i in range(5, 10): 
#     logger.info('------------------------------------------------')
#     logger.info('Analyzing CiteSeer')
#     logger.info('round : %s', i+1)
#     seed = 10 * (i+1)
#     logger.info('seed : %s', seed)
#     G = CiteSeer()
#     analyze_graph(G, seed)
    
#     logger.info('------------------------------------------------')
#     logger.info('Analyzing Cora')
#     logger.info('round : %s', i+1)
#     seed = 10 * (i+1)
#     logger.info('seed : %s', seed)
#     G = Cora()
#     analyze_graph(G, seed)

    logger.info('------------------------------------------------')
    logger.info('Analyzing connected small world')
    logger.info('round : %s', i+1)
    seed = 10 * (i+1)
    logger.info('seed : %s', seed)
    G = connSW(1000, 20, 0.1)
    analyze_graph(G, seed)

#     logger.info('------------------------------------------------')
#     logger.info('Analyzing random')
#     logger.info('round : %s', i+1)
#     seed = 10 * (i+1)
#     logger.info('seed : %s', seed)
#     G = rand(1000, 0.25, seed)
#     analyze_graph(G, seed)

#     logger.info('------------------------------------------------')
#     logger.info('Analyzing PubMed')
#     logger.info('round : %s', i+1)
#     seed = 10 * (i+1)
#     logger.info('seed : %s', seed)
#     G = PubMed()
#     analyze_graph(G, seed)

#     logger.info('------------------------------------------------')
#     logger.info('Analyzing coms')
#     logger.info('round : %s', i+1)
#     seed = 10 * (i+1)
#     logger.info('seed : %s', seed)
#     G = coms()
#     analyze_graph(G, seed)

#     logger.info('------------------------------------------------')
#     logger.info('Analyzing photo')
#     logger.info('round : %s', i+1)
#     seed = 10 * (i+1)
#     logger.info('seed : %s', seed)
#     G = photo()
#     analyze_graph(G, seed)
