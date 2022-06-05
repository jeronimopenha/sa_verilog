from math import ceil, log2
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

    def create_random_generator_11b(self) -> Module:
        # LFSR random generator based on Fibonacci's LFSR
        name = 'random_generator_11b'
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
                rnd(Cat(rnd[0:rnd.width - 1],
                    Not(Xor(Xor(Xor(rnd[10], rnd[9]), rnd[7]), rnd[1]))))
            )
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_cnc_memory(self, n_cells: int) -> Module:
        name = 'cnc_memory'
        if name in self.cache.keys():
            return self.cache[name]

        bits = ceil(log2(n_cells))

        m = Module(name)

        data_width = m.Parameter('data_width', bits)
        addr_width = m.Parameter('addr_width', bits)

        clk = m.Input('clk')
        we = m.Input('we')
        re = m.Input('re')
        
        waddr = m.Input('waddr', addr_width)
        din = m.Input('din', data_width)
        din_v = m.Input('din_v')

        raddr1 = m.Input('raddr1', addr_width)
        dout1 = m.OutputReg('dout1', data_width)
        dout1_v = m.OutputReg('dout1_v')

        raddr2 = m.Input('raddr2', addr_width)
        dout2 = m.OutputReg('dout2', data_width)
        dout2_v = m.OutputReg('dout2_v')

        #m.EmbeddedCode(
        #    '(* ramstyle = "AUTO, no_rw_check" *) reg  [data_width-1:0] mem[0:2**addr_width-1];')
        #m.EmbeddedCode('/*')
        mem_data = m.Reg('mem_data', data_width, Power(2, addr_width))
        mem_v = m.Reg('mem_v', data_width)
        #m.EmbeddedCode('*/')

        m.Always(Posedge(clk))(
            If(we)(
                mem_data[waddr](din),
                mem_v[waddr](din_v),
            ),
            If(re)(
                dout1(mem_data[raddr1]),
                dout1_v(mem_v[raddr1]),
                
                dout2(mem_data[raddr2]),
                dout2_v(mem_v[raddr2]),
            )
        )
        m.EmbeddedCode('//synthesis translate_off')

        i = m.Integer('i')
        m.Initial(
            dout1(0),
            dout2(0),
            For(i(0), i < Power(2, addr_width), i.inc())(
                mem_data[i](0),
                mem_v[i](0),
            ),
            #Systask('readmemh', init_file, mem_data)
        )
        m.EmbeddedCode('//synthesis translate_on')
        self.cache[name] = m
        return m

    def create_manhatan_dist_calc(self, n_cells:int) -> Module:
        name = 'manhatan_dist_calc'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        
        bits = ceil(log2(n_cells))

        clk = m.Input('clk')
        cell1 = m.Input('cell1', )

comp = SAComponents()

print(comp.create_cnc_memory(16).to_verilog())
#print(comp.create_random_generator_11b().to_verilog())