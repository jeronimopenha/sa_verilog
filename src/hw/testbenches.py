from veriloggen import *
from math import ceil, log2, sqrt
import src.hw.sa_components as _sa
import src.utils.util as _u


def create_threads_controller_test_bench(sa_comp: _sa.SAComponents) -> str:
    sa_graph = sa_comp.sa_graph
    n_cells = sa_comp.sa_graph.n_cells
    n_neighbors = sa_comp.n_neighbors
    align_bits = sa_comp.align_bits
    n_threads = sa_comp.n_threads

    name = "testbench_threads_controller_%dthreads_%dcells" % (
        n_threads, n_cells)
    if name in sa_comp.cache.keys():
        return sa_comp.cache[name]

    c_bits = ceil(log2(n_cells))
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits
    node_bits = c_bits
    lines = columns = int(sqrt(n_cells))
    w_bits = t_bits+c_bits+node_bits+1
    dist_bits = c_bits + ceil(log2(n_neighbors*2))

    # FIXME
    # 1º - Create the memory archives: c-n n-c and neighbors
    # create_rom_files(sa_comp)

    # 2º - Create testbench and execute it

    # TEST BENCH MODULE
    m = Module(name)
    clk = m.Reg('clk')
    rst = m.Reg('rst')
    start = m.Reg('start')

    # threads controller
    par = []
    con = [
        ('clk', clk),
        ('rst', rst),
        ('start', start)
    ]
    aux = sa_comp.create_threads_controller()
    m.Instance(aux, aux.name, par, con)

    _u.initialize_regs(m, {"clk": 0, "rst": 1, "start": 0})
    simulation.setup_waveform(m)
    m.Initial(
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        rst(0),
        start(1),
        Delay(4000),
        Finish(),
    )
    m.EmbeddedCode("always #5clk=~clk;")
    # m.Always(Posedge(clk))(
    #    If(rnd_en)(
    #        Display("%d", rnd_rnd[0:4])
    #    )
    # )

    m.to_verilog(os.getcwd() + "/verilog/threads_controller.v")
    sim = simulation.Simulator(m, sim="iverilog")
    #rslt = sim.run()
    # print(rslt)


def create_sa_verilog_test_bench(sa_comp: _sa.SAComponents) -> str:
    sa_graph = sa_comp.sa_graph
    n_cells = sa_comp.sa_graph.n_cells
    n_neighbors = sa_comp.n_neighbors
    align_bits = sa_comp.align_bits
    n_threads = sa_comp.n_threads

    name = "testbench_sa_pipeline_%dthreads_%dcells" % (
        n_threads, n_cells)
    if name in sa_comp.cache.keys():
        return sa_comp.cache[name]

    c_bits = ceil(log2(n_cells))
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits
    node_bits = c_bits
    lines = columns = int(sqrt(n_cells))
    w_bits = t_bits+c_bits+node_bits+1
    dist_bits = c_bits + ceil(log2(n_neighbors*2))

    # FIXME
    # 1º - Create the memory archives: c-n n-c and neighbors
    _u.create_rom_files(sa_comp)

    # 2º - Create testbench and execute it

    # TEST BENCH MODULE
    m = Module(name)
    clk = m.Reg('clk')
    rst = m.Reg('rst')
    start = m.Reg('start')

    done = m.Wire('done')

    # threads controller
    par = []
    con = [
        ('clk', clk),
        ('rst', rst),
        ('start', start),
        ('n_exec', Int(1, 16, 10)),
        ('done', done)
    ]
    aux = sa_comp.create_sa_pipeline()
    m.Instance(aux, aux.name, par, con)

    _u.initialize_regs(m, {"clk": 0, "rst": 1, "start": 0})
    simulation.setup_waveform(m)
    m.Initial(
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        rst(0),
        start(1),
        #Delay(4000),
        #Finish(),
    )

    m.Always(Posedge(clk))(
        If(done)(
            Finish()
        )
    )

    m.EmbeddedCode("always #5clk=~clk;")
    # m.Always(Posedge(clk))(
    #    If(rnd_en)(
    #        Display("%d", rnd_rnd[0:4])
    #    )
    # )

    m.to_verilog(os.getcwd() + '/verilog/sa_verilog_test.v')
    sim = simulation.Simulator(m, sim="iverilog")
    rslt = sim.run()
    print(rslt)
    _u.create_dot_from_rom_files(
        os.getcwd() + '/rom/c_n.rom','ini_th', os.getcwd() + '/rom/', n_threads, n_cells)
    _u.create_dot_from_rom_files(
        os.getcwd() + '/rom/c_n_out.rom','end_th', os.getcwd() + '/rom/', n_threads, n_cells)
    print(sa_graph.neighbors)
