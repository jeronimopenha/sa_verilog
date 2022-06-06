from math import ceil, log2
from veriloggen import *
from utils import initialize_regs


class SAComponents:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, n_cells: int = 16, n_neighbors: int = 5, align_bits: int = 8):
        self.cache = {}
        self.n_cells = n_cells
        self.align_bits = align_bits

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

        # m.EmbeddedCode(
        #    '(* ramstyle = "AUTO, no_rw_check" *) reg  [data_width-1:0] mem[0:2**addr_width-1];')
        # m.EmbeddedCode('/*')
        mem_data = m.Reg('mem_data', data_width, Power(2, addr_width))
        mem_v = m.Reg('mem_v', data_width)
        # m.EmbeddedCode('*/')

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

    def create_graph_memory(self, n_cells: int, n_neighbors: int) -> Module:
        name = 'graph_memory'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        bits_width = ceil(log2(n_cells))
        bits_word = ceil((ceil(log2(n_cells)) + 1) /
                         self.align_bits) * self.align_bits * n_neighbors

        clk = m.Input('clk')

        rd = m.Input('rd')
        node1 = m.Input('node1', bits_width)
        neighbors1_out = m.OutputReg('neighbors1_out', bits_word)

        node2 = m.Input('node2', bits_width)
        neighbors2_out = m.OutputReg(
            'neighbors2_out', bits_word)

        wr = m.Input('wr')
        wr_addr = m.Input('wr_addr', bits_width)
        data_in = m.Input('data_in', bits_word)

        mem_neighbors = m.Reg('mem_neighbors', bits_word)

        m.Always(Posedge(clk))(
            If(wr)(
                mem_neighbors[wr_addr](data_in)
            ),
            If(rd)(
                neighbors1_out(mem_neighbors[node1]),
                neighbors1_out(mem_neighbors[node2]),
            )
        )

        m.EmbeddedCode('//synthesis translate_off')

        i = m.Integer('i')
        m.Initial(
            neighbors1_out(0),
            neighbors2_out(0),
            For(i(0), i < Power(2, bits_width), i.inc())(
                mem_neighbors[i](0),
            ),
            #Systask('readmemh', init_file, mem_data)
        )
        m.EmbeddedCode('//synthesis translate_on')
        self.cache[name] = m
        return m

    def create_manhatan_dist_calc(self, n_cells: int) -> Module:
        name = 'manhatan_dist_calc'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        bits = ceil(log2(n_cells))/8

        clk = m.Input('clk')
        cell1 = m.Input('cell1', bits)
        cell2 = m.Input('cell2', bits)
        manhatan = m.OutputReg('manhatan', bits)

        parc_1 = m.Reg('parc_1', bits)
        parc_2 = m.Reg('parc_2', bits)
        l1 = m.Wire('l1', bits)
        l2 = m.Wire('l2', bits)
        c1 = m.Wire('c1', bits)
        c2 = m.Wire('c2', bits)

        l1.assign(Cat(Int(0, int(bits/2), 2), cell1[0:int(bits/2)]))
        l2.assign(Cat(Int(0, int(bits/2), 2), cell2[0:int(bits/2)]))
        c1.assign(Cat(Int(0, int(bits/2), 2), cell1[int(bits/2):cell1.width]))
        c2.assign(Cat(Int(0, int(bits/2), 2), cell2[int(bits/2):cell2.width]))

        # TODO tentar otimizar para 1 clock
        m.Always(Posedge(clk))(
            parc_1(Mux(l1 < l2, l2-l1, l1-l2)),
            parc_2(Mux(c1 < c2, c2-c1, c1-c2)),
            manhatan(parc_1 + parc_2),
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_sa_thread(self, n_cells: int, n_neighbors: int) -> Module:
        name = 'sa_thread'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        clk = m.Input('clk')
        rst = m.Input('rst')

        self.cache[name] = m
        return m


comp = SAComponents()

comp.create_manhatan_dist_calc(16).to_verilog("manhatan.v")
#comp.create_graph_memory(16, 5).to_verilog("graph_memory.v")
