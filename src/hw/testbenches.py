import random

from veriloggen import *

from src.hw.sa_components import SAComponents
from src.utils import util
from math import ceil, log2


def create_threads_test_bench():
    comp = SAComponents()
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
    aux = comp.create_threads_controller()
    m.Instance(aux, aux.name, par, con)

    util.initialize_regs(m, {"clk": 0, "rst": 1, "start": 0})
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


def create_sa_test_bench(dot: str):
    # FIXME
    n_threads = 1
    sa_graph = util.SaGraph(dot)
    c_n = []
    n_c = []
    for i in range(n_threads):
        c_n_i, n_c_i = sa_graph.get_initial_grid()
        c_n.append(c_n_i)
        n_c.append(n_c_i)
    comp = SAComponents(sa_graph=sa_graph)

    # TEST BENCH MODULE
    m = Module('test_sa')
    clk = m.Reg('clk')
    rst = m.Reg('rst')
    start = m.Reg('start')

    n_cells = comp.n_cells
    c_bits = ceil(log2(n_cells))
    m_width = c_bits * 2
    #n_threads = comp.n_threads
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits

    t_done = m.Wire('t_done')
    t_th = m.Wire('t_th', t_bits)
    t_v = m.Wire('t_v')
    t_cell1 = m.Wire('t_cell1', c_bits)
    t_cell2 = m.Wire('t_cell2', c_bits)

    # threads controller
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
    aux = comp.create_threads_controller()
    m.Instance(aux, aux.name, par, con)

    # cells to nodes
    # the reading is done first for the firs cell and after for
    # the second cell and this will happen over the pipeline

    # pipeline regs
    c1p_t_done = m.Wire('c1p_t_done')
    c1p_t_th = m.Wire('c1p_t_th', t_bits)
    c1p_t_v = m.Wire('c1p_t_v')
    c1p_t_cell1 = m.Wire('c1p_t_cell1', c_bits)
    c1p_t_cell2 = m.Wire('c1p_t_cell2', c_bits)

    m.Always(Posedge(clk))(
        c1p_t_done(t_done),
        c1p_t_th(t_th),
        c1p_t_v(t_v),
        c1p_t_cell1(t_cell1),
        c1p_t_cell2(t_cell2),
    )

    c1_rd = m.Wire('')
    c1_rd_addr = m.Wire('')
    c1_out = m.Wire('')
    c1_wr = m.Wire('')
    c1_wr_addr = m.Wire('')
    c1_wr_data = m.Wire('')

    # FIXME
    c1_wr.assign(0)
    c1_wr_addr.assign(0)
    c1_wr_data.assign(0)
    par = []
    con = [
        ('clk', clk),
        ('rd', c1_rd),
        ('rd_addr1', c1_rd_addr),
        ('out1', c1_out),
        ('wr', c1_wr),
        ('wr_addr', c1_wr_addr),
        ('wr_data', c1_wr_data),
    ]
    aux = comp.create_threads_controller()
    m.Instance(aux, aux.name, par, con)

    util.initialize_regs(m, {"clk": 0, "rst": 1, "start": 0})
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
