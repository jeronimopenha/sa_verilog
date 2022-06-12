from math import ceil, log2, sqrt
from veriloggen import *
from utils import initialize_regs


class SAComponents:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        n_cells: int = 16,
        n_threads: int = 4,
        n_neighbors: int = 5,
        align_bits: int = 8,
    ):
        self.cache = {}
        self.n_cells = n_cells
        self.n_neighbors = n_neighbors
        self.align_bits = align_bits
        self.n_threads = n_threads

    def create_memory_2r_1w(self, width, depth) -> Module:
        name = "mem_2r_1w_width%d_depth%d" % (width, depth)
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        init_file = m.Parameter('init_file', 'mem_file.txt')

        clk = m.Input("clk")
        rd = m.Input("rd")
        rd_addr1 = m.Input("rd_addr1", depth)
        rd_addr2 = m.Input("rd_addr2", depth)
        out1 = m.OutputReg("out1", width)
        out2 = m.OutputReg("out2", width)

        wr = m.Input("wr")
        wr_addr = m.Input("wr_addr", depth)
        wr_data = m.Input("wr_data", width)

        mem = m.Reg("mem", width, int(pow(2, depth)))

        m.Always(Posedge(clk))(
            If(rd)(out1(mem[rd_addr1]), out2(mem[rd_addr2])),
            If(wr)(mem[wr_addr](wr_data)),
        )

        m.EmbeddedCode('//synthesis translate_off')
        i = m.Integer('i')
        m.Initial(
            out1(0),
            out2(0),
            For(i(0), i < Power(2, depth), i.inc())(
                mem[i](0)
            ),
            Systask('readmemh', init_file, mem)
        )
        m.EmbeddedCode('//synthesis translate_on')
        self.cache[name] = m
        return m

    def create_threads(self) -> Module:
        n_cells = self.n_cells
        c_bits = ceil(log2(n_cells))
        m_width = c_bits * 2
        n_threads = self.n_threads
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits

        name = "_%d_threads_%d_cells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        clk = m.Input("clk")
        rst = m.Input("rst")
        start = m.Input("start")
        done = m.OutputReg("done")

        th = m.OutputReg("th", t_bits)
        v = m.OutputReg("v")
        cell1 = m.OutputReg("cell1", c_bits)
        cell2 = m.OutputReg("cell2", c_bits)

        m_rd = m.Reg("m_rd")
        m_rd_addr = m.Reg("m_rd_addr", t_bits)
        m_out = m.Wire("m_out", m_width)
        m_wr = m.Reg("m_wr")
        m_wr_addr = m.Reg("m_wr_addr", t_bits)
        m_wr_data = m.Reg("m_wr_data", m_width)
        sum = m.Wire('sum', m_width)
        init_mem = m.Reg("init_mem", n_threads)
        done_mem = m.Reg("done_mem", n_threads)

        p_addr = m.Reg('p_addr', t_bits)
        p_rd = m.Reg('p_rd')

        m.Always(Posedge(clk))(
            If(rst)(
                done(0),
            ).Else(
                done(Uand(done_mem))
            ),
        )

        m.Always(Posedge(clk))(
            If(rst)(
                m_rd_addr(n_threads-1),
                m_rd(0),
                p_rd(0),
                p_addr(0),
            ).Elif(start)(
                m_rd(1),
                p_addr(m_rd_addr),
                p_rd(m_rd),
                If(m_rd_addr == n_threads - 1)(
                    m_rd_addr(0),
                ).Else(
                    m_rd_addr.inc(),
                ),
            )
        )

        m.Always(Posedge(clk))(
            If(rst)(
                init_mem(0),
                done_mem(0),
                v(0),
                cell1(0),
                cell2(0),
            ).Else(
                If(p_rd)(
                    If(init_mem[p_addr])(
                        cell1(m_out[0:cell1.width]),
                        cell2(m_out[cell1.width:m_out.width]),
                        m_wr_data(m_out + 1),
                    ).Else(
                        init_mem[p_addr](1),
                        cell1(1),
                        cell2(0),
                        m_wr_data(2),
                    ),
                    If(m_out == (n_cells * n_cells)-2)(
                        done_mem[p_addr](1),
                    ),
                    m_wr_addr(p_addr),
                    m_wr(1),
                    th(p_addr),
                    v(Mux(done_mem[p_addr], 0, 1)),
                ),
            )
        )

        par = []
        con = [
            ("clk", clk),
            ("rd", m_rd),
            ("rd_addr1", m_rd_addr),
            ("out1", m_out),
            ("wr", m_wr),
            ("wr_addr", m_wr_addr),
            ("wr_data", m_wr_data),
        ]
        aux = self.create_memory_2r_1w(m_width, t_bits)
        m.Instance(aux, aux.name, par, con)

        initialize_regs(m)

        self.cache[name] = m
        return m

    def creat_cell_node_mem_pipe(self) -> Module:
        n_cells = self.n_cells
        c_bits = ceil(log2(n_cells))
        n_threads = self.n_threads
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        m_depth = c_bits + t_bits
        m_width = c_bits +

        name = "_%d_threads_%d_cells_cell_node_mem_pipe" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        clk = m.Input('clk')
        cell1 = m.Input('cell1', c_bits)
        cell2 = m.Input('cell2', c_bits)

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_sa_pipeline(self):
        n_cells = self.n_cells
        bits = ceil(log2(n_cells))
        m_depth = bits * 2
        n_threads = self.n_threads
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits


# comp = SAComponents()
# comp.create_thread().to_verilog('thread.v')
# comp.create_arbiter().to_verilog('arbiter.v')
# comp.create_memory_2r_1w(32, 8).to_verilog('memory_2r_1w.v')
# comp.create_threads().to_verilog("threads.v")
