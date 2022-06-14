import networkx as nx
from math import ceil, sqrt, log2, exp
from src.utils import util
import random


def sa(dot: str, n_grids: int, t_min: int):
    random.seed(0)
    sa_graph = util.SaGraph(dot)
    c_n = []
    n_c = []
    for i in range(n_grids):
        c_n_i, n_c_i = sa_graph.get_initial_grid()
        c_n.append(c_n_i)
        n_c.append(n_c_i)

    t = 100.0
    # execução do SA
    for ng in range(n_grids):
        actual_cost = sa_graph.get_total_cost(c_n[ng], n_c[ng])
        print(actual_cost)
        # while t >= t_min:
        for i in range(t_min):
            for cell1 in range(sa_graph.n_cells):
                for cell2 in range(sa_graph.n_cells):
                    if cell1 == cell2:
                        continue
                    next_cost = actual_cost
                    node1 = c_n[ng][cell1]
                    node2 = c_n[ng][cell2]
                    if node1 == None and node2 == None:
                        continue
                    cost_cell1_b, cost_cell1_a, cost_cell2_b, cost_cell2_a = sa_graph.get_cost(
                        n_c[ng], node1, node2, cell1, cell2)
                    next_cost -= cost_cell1_b
                    next_cost -= cost_cell2_b
                    next_cost += cost_cell1_a
                    next_cost += cost_cell2_a

                    #valor = exp((-1*(d_a - d_b)/t))
                    #rnd = random.random()

                    if next_cost < actual_cost:  # or rnd <= valor:
                        if node1 is not None:
                            n_c[ng][node1] = cell2

                        if node2 is not None:
                            n_c[ng][node2] = cell1
                        c_n[ng][cell1], c_n[ng][cell2] = c_n[ng][cell2], c_n[ng][cell1]
                        actual_cost = next_cost
                    print(actual_cost)
            t *= 0.99
    print(sa_graph.get_total_cost(c_n[ng], n_c[ng]))
    a = 1
