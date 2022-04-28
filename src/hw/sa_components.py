from veriloggen import *
from math import log2, ceil
from utils import initialize_regs


class SAComponents:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.cache = {}

    def create_memory_drd_sync(self):
        name = 'memory_drd_sync'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        init_file = m.Parameter('init_file', 'mem_file.txt')
        data_width = m.Parameter('data_width', 32)
        addr_width = m.Parameter('addr_width', 8)

        clk = m.Input('clk')

        we = m.Input('we')
        re = m.Input('re')

        raddr1 = m.Input('raddr1', addr_width)
        raddr2 = m.Input('raddr2', addr_width)
        waddr = m.Input('waddr', addr_width)
        din = m.Input('din', data_width)
        dout1 = m.OutputReg('dout1', data_width)
        dout2 = m.OutputReg('dout2', data_width)

        m.EmbeddedCode('(* ramstyle = "AUTO, no_rw_check" *) reg  [data_width-1:0] mem[0:2**addr_width-1];')
        m.EmbeddedCode('/*')
        mem = m.Reg('mem', data_width, Power(2, addr_width))
        m.EmbeddedCode('*/')

        m.Always(Posedge(clk))(
            If(we)(
                mem[waddr](din)
            ),
            If(re)(
                dout1(mem[raddr1]),
                dout2(mem[raddr2]),
            )
        )
        m.EmbeddedCode('//synthesis translate_off')

        i = m.Integer('i')
        m.Initial(
            dout1(0),
            dout2(0),
            For(i(0), i < Power(2, addr_width), i.inc())(
                mem[i](0)
            ),
            Systask('readmemh', init_file, mem)
        )
        m.EmbeddedCode('//synthesis translate_on')
        self.cache[name] = m
        return m

    def create_distance_rom_memory(self, lines, columns, distance_matrix):
        name = 'distance_rom_memory_%d_%d' % (lines, columns)
        if name in self.cache.keys():
            return self.cache[name]

        # shortest Manhattan distance
        distance_width = ceil(log2(lines + columns))

        m = Module(name)

        clk = m.Input('clk')
        re = m.Input('re')
        rd_pe_1 = m.Input('rd_pe_1', ceil(log2(lines * columns)))
        rd_pe_2 = m.Input('rd_pe_2', ceil(log2(lines * columns)))
        pe_1_out = m.Output('pe_1_out', lines * columns * distance_width)
        pe_2_out = m.Output('pe_2_out', lines * columns * distance_width)

        # Memory
        m.EmbeddedCode('//Memory')
        mem = m.Wire('mem', pe_1_out.width, lines * columns)
        m.EmbeddedCode('//---------------')
        # --------------

        # Reading the memory
        m.EmbeddedCode('//Reading the memory')
        m.Always(Posedge(clk))(
            If(re)(
                pe_1_out(mem[rd_pe_1]),
                pe_2_out(mem[rd_pe_2]),
            )
        )
        m.EmbeddedCode('//---------------')
        # ----------------------

        # Memory Content
        m.EmbeddedCode('//Memory Content')
        line_counter = 0
        for l in distance_matrix:
            s = "{"
            for c in l:
                s = s + str(c) + ","
            s = s[:-1]
            s = s + "}"
            mem[line_counter].assign(EmbeddedCode(s))
            line_counter = line_counter + 1

        m.EmbeddedCode('//---------------')
        # ----------------------

        initialize_regs(m)
        self.cache[name] = m
        return m

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

    # todo
    def create_nd_pe_rel_controller(self, qty_pes):
        name = 'node_pe_rel_controller'
        if name in self.cache.keys():
            return self.cache[name]

        node_add_width = ceil(log2(qty_pes))
        node_width = node_add_width

        m = Module(name)

        clk = m.Input('clk')
        rst = m.Input('rst')
        re = m.Input('re')
        rd_nd_1 = m.Input('rd_nd_1', node_add_width)
        pe1_rd_out = m.Output('pe1_rd_out', node_width)
        pe1_rd_out_v = m.Output('pe1_rd_out_v')
        rd_nd_2 = m.Input('rd_nd_2', node_add_width)
        pe2_rd_out = m.Output('pe2_rd_out', node_width)
        pe2_rd_out_v = m.Output('pe2_rd_out_v')
        we = m.Input('we')
        wr_addr = m.Input('wr_addr', node_add_width)
        wr_data = m.Input('wr_data', node_width)
        wr_data_v = m.Input('wr_data_v', node_width)

        rdy = m.Output('rdy')

        mem_v_wr_data = m.Wire('mem_v_wr_data')
        mem_v_we = m.Wire('mem_v_we')
        mem_v_waddr = m.Wire('mem_v_waddr', node_add_width)
        init_counter = m.Reg('init_counter', node_add_width + 1)
        init_we = m.Reg('init_we')
        init_wr_data = m.Wire('init_wr_data')
        init_wr_addr = m.Wire('init_wr_addr')

        init_wr_data.assign(0)
        init_wr_addr.assign(init_counter)

        mem_v_wr_data.assign(Mux(rdy, wr_data_v, init_wr_data))
        mem_v_waddr.assign(Mux(rdy, wr_addr, init_wr_addr))
        mem_v_we.assign(Mux(rdy, we, init_we))

        m.Always(Posedge(clk))(
            If(rst)(
                rdy(0),
                init_counter(0),
                init_we(0)
            ).Elif(Not(rdy))(
                If(init_counter == qty_pes - 1)(
                    rdy(1),
                    init_we(0),
                ).Else(
                    init_we(1),
                    init_counter.inc(),
                ),
            )
        )

        par = [('data_width', 1), ('addr_width', node_add_width)]
        con = [('clk', clk), ('we', mem_v_we), ('re', re), ('raddr1', rd_nd_1), ('raddr2', rd_nd_2),
               ('waddr', mem_v_waddr), ('din', mem_v_wr_data), ('dout1', pe1_rd_out_v), ('dout2', pe2_rd_out_v)]
        meme_v = self.create_memory_drd_sync()
        m.Instance(meme_v, meme_v.name + "_valid", par, con)

        par = [('data_width', node_width), ('addr_width', node_add_width)]
        con = [('clk', clk), ('we', we), ('re', re), ('raddr1', rd_nd_1), ('raddr2', rd_nd_2), ('waddr', wr_addr),
               ('din', wr_data), ('dout1', pe1_rd_out), ('dout2', pe1_rd_out)]
        meme_d = self.create_memory_drd_sync()
        m.Instance(meme_d, meme_d.name, par, con)

        initialize_regs(m)
        self.cache[name] = m
        return m

    # todo
    def create_node_connections_memory(self, qty_nodes):
        name = 'node_pe_rel_memory'
        if name in self.cache.keys():
            return self.cache[name]

        config_word_width = 8
        distance_width = 8

        m = Module(name)

        clk = m.Input('clk')
        rst = m.Input('rst')
        input_config_valid = m.Input('input_config_valid')
        input_config = m.Input('input_config', config_word_width)
        re = m.Input('re')
        rd_pe_1 = m.Input('rd_pe_1', ceil(log2(qty_nodes)))
        rd_pe_2 = m.Input('rd_pe_2', ceil(log2(qty_nodes)))
        pe_1_out = m.Output('pe_1_out', qty_nodes * distance_width)
        pe_2_out = m.Output('pe_2_out', qty_nodes * distance_width)
        rdy = m.Output('rdy')

        # input_Registers
        m.EmbeddedCode('//input_Registers')
        input_config_valid_r = m.Reg('input_config_valid_r')
        input_config_r = m.Reg('input_config_r', input_config.width)
        re_r = m.Reg('re_r')
        rd_pe_1_r = m.Reg('rd_pe_1_r', rd_pe_1.width)
        rd_pe_2_r = m.Reg('rd_pe_2_r', rd_pe_2.width)
        m.EmbeddedCode('//---------------')
        # ---------------

        # Config controler
        m.EmbeddedCode('//Config controler')
        config_column_counter = m.Reg('config_column_counter', qty_nodes)
        config_data = m.Reg('config_data', qty_nodes * config_word_width)
        mem_we = m.Reg('mem_we')
        mem_waddr = m.Reg('mem_waddr', ceil(log2(qty_nodes)))
        m.EmbeddedCode('//---------------')
        # ---------------

        # Registering the inputs
        m.EmbeddedCode('//Registering the inputs')
        m.Always(Posedge(clk))(
            input_config_valid_r(input_config_valid),
            input_config_r(input_config),
            re_r(re),
            rd_pe_1_r(rd_pe_1),
            rd_pe_2_r(rd_pe_2),
        )
        m.EmbeddedCode('//---------------')
        # ----------------------

        # Configuration algorithm
        m.EmbeddedCode('//Configuration algorithm')
        m.Always(Posedge(clk))(
            If(rst)(
                rdy(0),
                config_column_counter(1),
                mem_we(0),
                mem_waddr(0),
            ).Elif(input_config_valid_r)(
                config_data(Cat(input_config, config_data[config_word_width:config_data.width])),
                If(config_column_counter[qty_nodes - 1])(
                    mem_we(1),
                    config_column_counter(
                        Cat(config_column_counter[0:config_column_counter.width - 1], Int(1, 1, 2))),
                ).Else(
                    mem_we(0),
                    config_column_counter(
                        Cat(config_column_counter[0:config_column_counter.width - 1], Int(0, 1, 2))),
                ),
            ),
            If(mem_we)(
                mem_waddr.inc(),
            ),
        )
        m.EmbeddedCode('//---------------')
        # ----------------------

        # Main memory to be used for the distance memory
        m.EmbeddedCode('//Main memory to be used for the distance memory')
        par = [('data_width', qty_nodes * distance_width), ('addr_width', ceil(log2(qty_nodes)))]
        con = [('clk', clk), ('we', mem_we), ('re', re_r), ('raddr1', rd_pe_1_r), ('raddr2', rd_pe_2_r),
               ('waddr', mem_waddr), ('din', config_data), ('dout1', pe_1_out), ('dout2', pe_2_out)]
        memory_dual_read = self.create_memory_drd_sync()
        m.Instance(memory_dual_read, memory_dual_read.name, par, con)
        m.EmbeddedCode('//---------------')
        # ----------------------

        self.cache[name] = m
        return m


comp = SAComponents()

# node-pe relational memory
comp.create_nd_pe_rel_controller(16).to_verilog('test.v')

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
