from veriloggen import *
from math import ceil, log2, sqrt
import subprocess
import pygraphviz as pgv
import networkx as nx
import random


# import src.hw.sa_components as _sa_comp

# from src.hw.sa_components import SAComponents


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
        self.get_dot_vars()

    def reset_random(self):
        random.seed(0)

    def get_initial_grid(self) -> list():
        n_nodes = len(self.nodes)
        n_edges = len(self.edges)

        c_n = [None for i in range(self.n_cells)]
        n_c = [None for i in range(self.n_cells)]

        unsorted_nodes = [n for n in self.nodes]
        unsorted_cells = [i for i in range(self.n_cells)]

        while len(unsorted_nodes) > 0:
            r_n = random.randint(0, (len(unsorted_nodes) - 1))
            r_c = random.randint(0, (len(unsorted_cells) - 1))
            n = unsorted_nodes[r_n]
            c = unsorted_cells[r_c]

            c_n[c] = self.nodes_to_idx[n]
            n_c[c_n[c]] = c
            unsorted_cells.pop(r_c)
            unsorted_nodes.pop(r_n)

        return c_n, n_c

    def get_dot_vars(self):
        dot = self.dot
        # g = nx.Graph(nx.nx_pydot.read_dot(dot))
        gv = pgv.AGraph(dot, strict=False, directed=True)
        g = nx.DiGraph(gv)
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
        # print(sorted(costs.items(), key=lambda x: x[0]))
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

    def get_manhattan_distance(self, cell1: int, cell2: int) -> int:
        cell1_x = cell1 % self.n_cells_sqrt
        cell1_y = cell1 // self.n_cells_sqrt
        cell2_x = cell2 % self.n_cells_sqrt
        cell2_y = cell2 // self.n_cells_sqrt
        return abs(cell1_y - cell2_y) + abs(cell1_x - cell2_x)


def to_bytes_string_list(conf_string):
    list_ret = []
    for i in range(len(conf_string), 0, -8):
        list_ret.append(conf_string[i - 8: i])
    return list_ret


def state(val, size):
    return format(val, "0%dx" % size)


def initialize_regs(module: Module, values=None):
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


def create_rom_files(sa_comp, path: str):
    sa_graph = sa_comp.sa_graph
    n_cells = sa_comp.sa_graph.n_cells
    n_neighbors = sa_comp.n_neighbors
    align_bits = sa_comp.align_bits
    n_threads = sa_comp.n_threads

    c_bits = ceil(log2(n_cells))
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits
    node_bits = c_bits
    lines = columns = int(sqrt(n_cells))
    w_bits = t_bits + c_bits + node_bits + 1
    dist_bits = c_bits + ceil(log2(n_neighbors * 2))

    sa_graph.reset_random()

    c_n = []
    n_c = []
    for i in range(n_threads):
        c_n_i, n_c_i = sa_graph.get_initial_grid()
        c_n.append(c_n_i)
        n_c.append(n_c_i)

    cn_str_f = '{:0%db}' % (node_bits + 1)
    nc_str_f = '{:0%db}' % (c_bits)
    n_str_f = '{:0%db}' % (node_bits + 1)
    t_str = '{:0%db}' % (t_bits)

    cn_w = []  # [cn_str_f.format(0) for i in range(n_cells)]
    nc_w = []  # [nc_str_f.format(0) for i in range(n_cells)]
    p_w = []  # [p_str_f.format(0) for i in range(n_cells)]
    n_w = []
    for t in range(pow(2, ceil(sqrt(n_threads)))):
        cn_w.append([cn_str_f.format(0)
                     for i in range(ceil(sqrt(n_cells)) * ceil(sqrt(n_cells)))])
        nc_w.append([nc_str_f.format(0)
                     for i in range(ceil(sqrt(n_cells)) * ceil(sqrt(n_cells)))])

    for c in range(pow(2, ceil(sqrt(n_cells)))):
        n_w.append([n_str_f.format(0) for i in range(n_neighbors)])
    for k in sa_graph.neighbors.keys():
        idx = 0
        for n in sa_graph.neighbors[k]:
            n_w[k][idx] = n_str_f.format((1 << node_bits) | n)
            idx += 1

    for t in range(len(c_n)):
        for cni in range(len(c_n[t])):
            if c_n[t][cni] is not None:
                cn_w[t][cni] = cn_str_f.format((1 << node_bits) | c_n[t][cni])

    for t in range(len(n_c)):
        for nci in range(len(n_c[t])):
            if n_c[t][nci] is not None:
                nc_w[t][nci] = nc_str_f.format(n_c[t][nci])

    with open(path + '/th.rom', 'w') as f:
        for i in range(pow(2, ceil(sqrt(n_threads)))):
            f.write(t_str.format(0))
            f.write('\n')
        f.close()

    with open(path + '/n_c.rom', 'w') as f:
        for t in nc_w:
            for d in t:
                f.write(d)
                f.write('\n')
        if n_threads == 1:
            for d in range(n_cells):
                f.write(nc_str_f.format(0))
                f.write('\n')
        f.close()
    with open(path + '/c_n.rom', 'w') as f:
        for t in cn_w:
            for d in t:
                f.write(d)
                f.write('\n')
        if n_threads == 1:
            for d in range(n_cells):
                f.write(cn_str_f.format(0))
                f.write('\n')
        f.close()

    for i in range(n_neighbors):
        with open(path + '/n%d.rom' % i, 'w') as f:
            for c in range(n_cells):
                f.write(n_w[c][i])
                f.write('\n')
            f.close()


def create_dot_from_rom_files(rom_file: str, prefix: str, output_path: str, n_threads: int, n_cells: int):
    c_bits = ceil(log2(n_cells))
    output_dot_files = [prefix + '%d.dot' % i for i in range(n_threads)]
    dot_head = 'digraph layout{\n rankdir=TB;\n splines=ortho;\n node [style=filled shape=square fixedsize=true width=0.6];\n'
    dot_foot = 'edge [constraint=true, style=invis];\n'
    sqrt_cells = ceil(sqrt(n_cells))

    for i in range(sqrt_cells):
        for j in range(sqrt_cells):
            dot_foot = dot_foot + '%d' % (j * sqrt_cells + i)
            if (j + 1) % sqrt_cells == 0:
                dot_foot = dot_foot + ';\n'
            else:
                dot_foot = dot_foot + ' -> '

    for i in range(n_cells):
        if i % sqrt_cells == 0:
            dot_foot = dot_foot + 'rank = same {'
        dot_foot = dot_foot + '%d' % i
        if (i + 1) % sqrt_cells == 0:
            dot_foot = dot_foot + '};\n'
        else:
            dot_foot = dot_foot + ' -> '

    dot_foot = dot_foot + '}'

    str_out = [dot_head for i in range(n_threads)]
    file_lines = []
    with open(rom_file) as f:
        file_lines = f.readlines()
        f.close()
    for t in range(n_threads):
        c = 0
        while (c < n_cells):
            c_content = file_lines.pop(0)
            if '//' in c_content:
                continue
            c_content = c_content.split('\n')[0]
            v = int(c_content, 16)
            v = v & (n_cells - 1)
            v = str(v)
            # print('%d[label="%s", fontsize=8, fillcolor="%s"];\n' % (
            #    c, '' if int(c_content, 16) == 0 else v, '#ffffff' if int(c_content, 16) == 0 else '#d9d9d9'))
            str_out[t] += '%d[label="%s", fontsize=8, fillcolor="%s"];\n' % (
                c, '' if int(c_content, 16) == 0 else v, '#ffffff' if int(c_content, 16) == 0 else '#d9d9d9')
            c += 1
        str_out[t] += dot_foot

    for t in range(n_threads):
        with open(output_path + output_dot_files[t], 'w') as f:
            f.write(str_out[t])
        f.close()
