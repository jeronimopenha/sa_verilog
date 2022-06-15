import networkx as nx
from math import ceil, sqrt, log2, exp
from src.utils import util
import random


def sa(dot: str, n_threads: int, t_min: int):
    random.seed(0)
    sa_graph = util.SaGraph(dot)
    c_n = []
    n_c = []
    for i in range(n_threads):
        c_n_i, n_c_i = sa_graph.get_initial_grid()
        c_n.append(c_n_i)
        n_c.append(n_c_i)

    t = 100.0
    # execução do SA
    for thread in range(n_threads):
        actual_cost = sa_graph.get_total_cost(c_n[thread], n_c[thread])
        print(actual_cost)
        while t >= t_min:
        #for i in range(t_min):
            for cell1 in range(sa_graph.n_cells):
                for cell2 in range(sa_graph.n_cells):
                    #cell1 = random.randint(0,sa_graph.n_cells-1)
                    #cell2 = random.randint(0,sa_graph.n_cells-1)
                    if cell1 == cell2:
                        continue
                    next_cost = actual_cost
                    node1 = c_n[thread][cell1]
                    node2 = c_n[thread][cell2]
                    if node1 == None and node2 == None:
                        continue
                    cost_cell1_b, cost_cell1_a, cost_cell2_b, cost_cell2_a = sa_graph.get_cost(
                        n_c[thread], node1, node2, cell1, cell2)
                    next_cost -= cost_cell1_b
                    next_cost -= cost_cell2_b
                    next_cost += cost_cell1_a
                    next_cost += cost_cell2_a

                    #valor = abs(next_cost - actual_cost)
                    #valor = exp((-1 * valor / t))
                    #rnd = random.random()
                    '''
                    try:
                        valor = exp((-1 * (next_cost - actual_cost) / t))
                    except:
                        valor = -1

                    rnd = random.random()
                    '''
                    if next_cost < actual_cost:# or rnd <= valor:
                        if node1 is not None:
                            n_c[thread][node1] = cell2

                        if node2 is not None:
                            n_c[thread][node2] = cell1
                        c_n[thread][cell1], c_n[thread][cell2] = c_n[thread][cell2], c_n[thread][cell1]
                        
                        actual_cost = next_cost #= sa_graph.get_total_cost(c_n[thread], n_c[thread])
                    
                print(actual_cost)
            t *= 0.999
    print(sa_graph.get_total_cost(c_n[thread], n_c[thread]))
