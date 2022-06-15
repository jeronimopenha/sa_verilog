from veriloggen import *
from math import ceil, log2, sqrt
import subprocess
import networkx as nx
import random


class SaGraph:
    def __init__(self, dot: str):
        self.dot = dot
        self.nodes = []
        self.n_nodes = 0
        self.edges = []
        self.nodes_to_idx = {}
        self.neighbors = {}
        self.n_cells = 0
        self.n_cells_sqrt = 0
        random.seed(0)
        self.get_dot_vars()

    def get_initial_grid(self) -> list():
        n_nodes = len(self.nodes)
        n_edges = len(self.edges)

        c_n = [None for i in range(self.n_cells)]
        n_c = [None for i in range(self.n_cells)]

        unsorted_nodes = [n for n in self.nodes]
        unsorted_cells = [i for i in range(self.n_cells)]

        while len(unsorted_nodes) > 0:
            r_n = random.randint(0, (len(unsorted_nodes)-1))
            r_c = random.randint(0, (len(unsorted_cells)-1))
            n = unsorted_nodes[r_n]
            c = unsorted_cells[r_c]

            c_n[c] = self.nodes_to_idx[n]
            n_c[c_n[c]] = c
            unsorted_cells.pop(r_c)
            unsorted_nodes.pop(r_n)

        return c_n, n_c

    def get_dot_vars(self):
        dot = self.dot
        g = nx.Graph(nx.nx_pydot.read_dot(dot))
        self.nodes = list(g.nodes)
        self.n_nodes = len(self.nodes)
        self.edges = list(g.edges)
        self.nodes_to_idx = {}
        self.neighbors = {}
        for i in range(self.n_nodes):
            self.nodes_to_idx[self.nodes[i]] = i

        for e in self.edges:
            if self.nodes_to_idx[e[0]] not in self.neighbors.keys():
                self.neighbors[self.nodes_to_idx[e[0]]] = []
            if self.nodes_to_idx[e[1]] not in self.neighbors.keys():
                self.neighbors[self.nodes_to_idx[e[1]]] = []
            self.neighbors[self.nodes_to_idx[e[0]]].append(
                self.nodes_to_idx[e[1]])
            self.neighbors[self.nodes_to_idx[e[1]]].append(
                self.nodes_to_idx[e[0]])

        self.n_cells_sqrt = ceil(sqrt(self.n_nodes))
        self.n_cells = pow(self.n_cells_sqrt, 2)

    def get_total_cost(self, c_n, n_c):
        costs = {}
        cost = 0
        for i in range(len(c_n)):
            if c_n[i] is None:
                continue
            cost_ = 0
            for n in self.neighbors[c_n[i]]:
                cost += self.get_manhattan_distance(i, n_c[n])
                cost_ += cost
            costs[c_n[i]] = cost_
        # print(costs)
        #print(sorted(costs.items(), key=lambda x: x[0]))
        return cost  # costs

    def get_cost(self, n_c, node1, node2, cell1, cell2):
        cost1_b = 0
        cost1_a = 0
        cost2_b = 0
        cost2_a = 0
        if node1 is not None:
            for n in self.neighbors[node1]:
                cost1_b += self.get_manhattan_distance(cell1, n_c[n])
                if cell2 == n_c[n]:
                    cost1_a += self.get_manhattan_distance(cell1, cell2)
                else:
                    cost1_a += self.get_manhattan_distance(cell2, n_c[n])
        if node2 is not None:
            for n in self.neighbors[node2]:
                cost2_b += self.get_manhattan_distance(cell2, n_c[n])
                if cell1 == n_c[n]:
                    cost2_a += self.get_manhattan_distance(cell2, cell1)
                else:
                    cost2_a += self.get_manhattan_distance(cell1, n_c[n])
        return cost1_b, cost1_a, cost2_b, cost2_a

    def get_manhattan_distance(self, idx1: int, idx2: int) -> int:
        cell1_x = idx1 % self.n_cells_sqrt
        cell1_y = idx1 // self.n_cells_sqrt
        cell2_x = idx2 % self.n_cells_sqrt
        cell2_y = idx2 // self.n_cells_sqrt
        return abs(cell1_y - cell2_y) + abs(cell1_x - cell2_x)


def print_matrix_to_str(c_n) -> str:
    s = []
    for i in range(len(c_n)):
        pass
    return " "


def to_bytes_string_list(conf_string):
    list_ret = []
    for i in range(len(conf_string), 0, -8):
        list_ret.append(conf_string[i - 8: i])
    return list_ret


def state(val, size):
    return format(val, "0%dx" % size)


def initialize_regs(module, values=None):
    regs = []
    if values is None:
        values = {}
    flag = False
    for r in module.get_vars().items():
        if module.is_reg(r[0]):
            regs.append(r)
            if r[1].dims:
                flag = True

    if len(regs) > 0:
        if flag:
            i = module.Integer("i_initial")
        s = module.Initial()
        for r in regs:
            if values:
                if r[0] in values.keys():
                    value = values[r[0]]
                else:
                    value = 0
            else:
                value = 0
            if r[1].dims:
                genfor = For(i(0), i < r[1].dims[0], i.inc())(r[1][i](value))
                s.add(genfor)
            else:
                s.add(r[1](value))


def commands_getoutput(cmd):
    byte_out = subprocess.check_output(cmd.split())
    str_out = byte_out.decode("utf-8")
    return str_out


def bits(n):
    if n < 2:
        return 1
    else:
        return int(ceil(log2(n)))
