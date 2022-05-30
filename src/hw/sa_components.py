from veriloggen import *
from utils import initialize_regs


class SAComponents:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.cache = {}

    def create_random_generator(self):
        # LFSR random generator based on Fibonacci's LFSR
        name = 'create_random_generator_11b'
        if name in self.cache.keys():
            return self.cache[name]

        bits = 11

        m = Module(name)
        clk = m.Input('clk')
        rst = m.Input('rst')
        en = m.Input('en')
        seed = m.Input('seed', bits)
        rnd = m.OutputReg('rnd', bits)

        m.Always(Posedge(clk))(
            If(rst)(
                rnd(seed)
            ).Elif(en)(
                rnd(Cat(rnd[0:rnd.width - 1], Not(Xor(Xor(Xor(rnd[10], rnd[9]), rnd[7]), rnd[1]))))
            )
        )

        initialize_regs(m)
        self.cache[name] = m
        return m



comp = SAComponents()

# node-pe relational memory
#comp.create_nd_pe_rel_controller(16).to_verilog('test.v')

'''
# random verilog creation test
comp.create_random_generator().to_verilog('test.v')
'''
'''
# distance memory verilog creation test

lines = 4
columns = 4
distance_matrix = []

for m in range(lines):
    for n in range(columns):
        line = []
        for l in range(lines):
            for c in range(columns):
                line.append(abs(m - l) + abs(n - c))
        distance_matrix.append(line)

comp.create_distance_rom_memory(lines, columns, distance_matrix).to_verilog('test.v')
'''
