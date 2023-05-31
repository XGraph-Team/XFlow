import random
import multiprocessing as mp
import networkx as nx
import utils

class InfWorker(mp.Process):
    def __init__(self, outQ, count, inf_function):
        super(InfWorker, self).__init__(target=self.start)
        self.outQ = outQ
        self.count = count
        self.inf_function = inf_function
        self.sum = 0

    def run(self):
        while self.count > 0:
            res = self.inf_function()
            self.sum += res
            self.count -= 1
            if self.count == 0:
                self.outQ.put(self.sum)

def create_worker(worker, num, task_num, inf_function):
    """
        create processes
        :param num: process number
        :param task_num: the number of tasks assigned to each worker
    """
    for i in range(num):
        worker.append(InfWorker(mp.Queue(), task_num, inf_function))
        worker[i].start()

def finish_worker(worker):
    """
    关闭所有子进程
    :return:
    """
    for w in worker:
        w.terminate()

class ICModel:

    def __init__(self, threshold_method='random', graph=None, seeds=None, worker_num=8, simulate_times=10000, p=0.5) -> None:
        self.tsm = threshold_method
        self.graph = graph
        self.worker_num = worker_num
        self.simulate_times = simulate_times
        self.seeds = seeds
        self.p = p

    def influence_func(self):
        assert self.graph != None and self.seeds != None
        if self.tsm == 'pp_random':
            return self.inf_pp_random_threshold()
        elif self.tsm == 'random':
            return self.inf_pp_fixed_random_threshold()
        elif self.tsm == 'avg':
            return self.inf_avg_threshold()

    # 影响概率pp事先计算，阈值随机
    def inf_pp_random_threshold(self):
        count = len(self.seeds)
        activity_set = set(self.seeds)
        active_nodes = set(self.seeds)
        while activity_set:
            new_activity_set = set()
            for seed in activity_set:
                for node in self.graph.neighbors(seed):
                    if node not in active_nodes:
                        if random.random() < self.graph[seed][node]['weight']:
                            active_nodes.add(node)
                            new_activity_set.add(node)
            count += len(new_activity_set)
            activity_set = new_activity_set
        return count

    # 影响概率pp固定，阈值随机
    def inf_pp_fixed_random_threshold(self):
        count = len(self.seeds)
        activity_set = set(self.seeds)
        active_nodes = set(self.seeds)
        while activity_set:
            new_activity_set = set()
            for seed in activity_set:
                for node in self.graph.neighbors(seed):
                    if node not in active_nodes:
                        if random.random() <= self.p:
                            active_nodes.add(node)
                            new_activity_set.add(node)
            count += len(new_activity_set)
            activity_set = new_activity_set
        return count

    def inf_avg_threshold(self):
        count = len(self.seeds)
        activity_set = set(self.seeds)
        active_nodes = set(self.seeds)
        node_threshold = {}
        node_weights = {}
        while activity_set:
            new_activity_set = set()
            for seed in activity_set:
                for node in self.graph.neighbors(seed):
                    if node not in active_nodes:
                        weight = self.graph[seed][node]['weight']
                        if node not in node_threshold:
                            node_threshold[node] = 0.5
                            node_weights[node] = 0
                        node_weights[node] += weight
                        if node_weights[node] >= node_threshold[node]:
                            active_nodes.add(node)
                            new_activity_set.add(node)
            count += len(new_activity_set)
            activity_set = new_activity_set
        return count

    def calculate_influence(self):
        worker = []
        create_worker(worker, self.worker_num, int(self.simulate_times / self.worker_num), self.influence_func)
        result = []
        for w in worker:
            result.append(w.outQ.get())
        finish_worker(worker)
        return sum(result) / self.simulate_times

def IC(g, S, p=0.1, mc=10000, method='random'):
    # graph: network 图
    # S: 种子集
    # p: 影响概率
    # mc: 模拟次数
    # method:
    #   - random: 影响概率pp固定，阈值随机
    #   - pp_random: 影响概率pp事先计算，阈值随机
    model = ICModel(threshold_method=method, graph=g, seeds=S, worker_num=8, simulate_times=mc, p=p)
    influence = model.calculate_influence()
    return influence

