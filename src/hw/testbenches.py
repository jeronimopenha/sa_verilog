import random
import networkx as nx

from veriloggen import *

from sa_components import SAComponents
from utils import initialize_regs
from math import ceil, log2


def create_threads_test_bench(comp: SAComponents):
    # TEST BENCH MODULE
    m = Module('test_threads')
    clk = m.Reg('clk')
    rst = m.Reg('rst')
    start = m.Reg('start')

    n_cells = comp.n_cells
    c_bits = ceil(log2(n_cells))
    m_width = c_bits * 2
    n_threads = comp.n_threads
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits

    t_done = m.Wire('t_done')
    t_th = m.Wire('t_th', t_bits)
    t_v = m.Wire('t_v')
    t_cell1 = m.Wire('t_cell1', c_bits)
    t_cell2 = m.Wire('t_cell2', c_bits)

    par = []
    con = [
        ('clk', clk),
        ('rst', rst),
        ('start', start),
        ('done', t_done),
        ('th', t_th),
        ('v', t_v),
        ('cell1', t_cell1),
        ('cell2', t_cell2)
    ]
    aux = comp.create_threads()
    m.Instance(aux, aux.name, par, con)

    initialize_regs(m, {"clk": 0, "rst": 1, "start": 0})
    simulation.setup_waveform(m)
    m.Initial(
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        rst(0),
        start(1),
        Delay(100000),
        Finish(),
    )
    m.EmbeddedCode("always #5clk=~clk;")
    # m.Always(Posedge(clk))(
    #    If(rnd_en)(
    #        Display("%d", rnd_rnd[0:4])
    #    )
    # )

    m.to_verilog("threads_test_bench_hw.v")
    sim = simulation.Simulator(m, sim="iverilog")
    rslt = sim.run()
    print(rslt)


def create_sa_test_bench(comp: SAComponents, dot: str):
    g = nx.Graph(nx.nx_pydot.read_dot(dot))
    print(g.nodes)
    print(g.edges)

    nodes = list(g.nodes)
    edges = list(g.edges)
    nodes_to_idx = {}
    neighbors = {}
    for i in range(len(nodes)):
        nodes_to_idx[nodes[i]] = i

    for e in edges:
        if nodes_to_idx[e[0]] not in neighbors.keys():
            neighbors[nodes_to_idx[e[0]]] = []
        if nodes_to_idx[e[1]] not in neighbors.keys():
            neighbors[nodes_to_idx[e[1]]] = []
        neighbors[nodes_to_idx[e[0]]].append(nodes_to_idx[e[1]])
        neighbors[nodes_to_idx[e[1]]].append(nodes_to_idx[e[0]])
    print(nodes_to_idx)
    print(neighbors)

    # TEST BENCH MODULE
    m = Module('test_threads')
    clk = m.Reg('clk')
    rst = m.Reg('rst')
    start = m.Reg('start')

    n_cells = comp.n_cells
    c_bits = ceil(log2(n_cells))
    m_width = c_bits * 2
    n_threads = comp.n_threads
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits

    t_done = m.Wire('t_done')
    t_th = m.Wire('t_th', t_bits)
    t_v = m.Wire('t_v')
    t_cell1 = m.Wire('t_cell1', c_bits)
    t_cell2 = m.Wire('t_cell2', c_bits)

    par = []
    con = [
        ('clk', clk),
        ('rst', rst),
        ('start', start),
        ('done', t_done),
        ('th', t_th),
        ('v', t_v),
        ('cell1', t_cell1),
        ('cell2', t_cell2)
    ]
    aux = comp.create_threads()
    m.Instance(aux, aux.name, par, con)

    initialize_regs(m, {"clk": 0, "rst": 1, "start": 0})
    simulation.setup_waveform(m)
    m.Initial(
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        rst(0),
        start(1),
        Delay(100000),
        Finish(),
    )
    m.EmbeddedCode("always #5clk=~clk;")
    # m.Always(Posedge(clk))(
    #    If(rnd_en)(
    #        Display("%d", rnd_rnd[0:4])
    #    )
    # )

    m.to_verilog("threads_test_bench_hw.v")
    sim = simulation.Simulator(m, sim="iverilog")
    rslt = sim.run()
    print(rslt)


comp = SAComponents()
# create_threads_test_bench(comp)
create_sa_test_bench(
    comp, "/home/jeronimo/Documentos/GIT/sa_verilog/dot/simple.dot")
