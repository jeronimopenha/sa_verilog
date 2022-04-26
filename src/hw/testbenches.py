import random

from veriloggen import *

from src.hw.sa_components import SAComponents
from src.hw.utils import initialize_regs


def create_random_generator_test_bench_hw():
    # TEST BENCH MODULE
    m = Module('test_random_generator')
    m.EmbeddedCode('\n//Standar I/O signals - Begin')
    clk = m.Reg('clk')
    rst = m.Reg('rst')
    m.EmbeddedCode('//Standar I/O signals - End')

    # Random needs - Begin
    m.EmbeddedCode('\n// Random needs - Begin')
    bits = 11
    rnd_en = m.Reg('rnd_en')
    rnd_rnd = m.Wire('rnd_rnd', bits)
    rnd_seed = m.Wire('rnd_seed', bits)
    rnd_seed.assign(Int(random.randint(0, pow(2, bits)), rnd_seed.width, 2))
    m.EmbeddedCode('// Random needs - end')
    # Random needs - End

    par = []
    con = [('clk', clk), ('rst', rst), ('en', rnd_en), ('seed', rnd_seed), ('rnd', rnd_rnd)]
    sa_comp = SAComponents()
    rnd_module = sa_comp.create_random_generator()
    m.Instance(rnd_module, rnd_module.name, par, con)

    initialize_regs(m, {'clk': 0, 'rst': 1, 'rnd_en': 0})
    simulation.setup_waveform(m)
    m.Initial(
        EmbeddedCode('@(posedge clk);'),
        EmbeddedCode('@(posedge clk);'),
        EmbeddedCode('@(posedge clk);'),
        rst(0),
        rnd_en(1),
        Delay(1000), Finish()
    )
    m.EmbeddedCode('always #5clk=~clk;')
    m.Always(Posedge(clk))(
        If(rnd_en)(
            Display("%d", rnd_rnd[0:4])
        )
    )

    m.to_verilog('random_generator_test_bench_hw.v')
    sim = simulation.Simulator(m, sim='iverilog')
    rslt = sim.run()
    print(rslt)


#create_random_generator_test_bench_hw()
