import random

from veriloggen import *

from src.hw.sa_components import SAComponents


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
    m.Instance(rnd_module,rnd_module.name,par,con)

    print(m.to_verilog())
    #m.to_verilog('../test_benches/grn_naive_pe_test_bench_' + str(
    #    len(self.grn_content.get_nodes_vector())) + '_nodes_' + str(int(pow(2, bits_grn))) + '_states.v')
    #sim = simulation.Simulator(m, sim='iverilog')
    #rslt = sim.run()
    #print(rslt)


create_random_generator_test_bench_hw()