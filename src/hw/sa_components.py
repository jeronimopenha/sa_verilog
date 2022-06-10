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

    def create_memory_2r_1w(self, width, depth):
        name = "mem_2r_1w_w%d_d%d" % (width, depth)
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        clk = m.Input("clk")
        rd = m.Input("rd")
        rd_addr1 = m.Input("rd_addr1", depth)
        rd_addr2 = m.Input("rd_addr2", depth)
        out_1 = m.OutputReg("out_1", width)
        out_2 = m.OutputReg("out_2", width)

        wr = m.Input("wr")
        wr_addr = m.Input("wr_addr", depth)
        wr_data = m.Input("wr_data", width)

        mem = m.Reg("mem", width, int(pow(2, depth)))

        m.Always(Posedge(clk))(
            If(rd)(out_1(mem[rd_addr1]), out_2(mem[rd_addr2])),
            If(wr)(mem[wr_addr](wr_data)),
        )

        #initialize_regs(m)
        self.cache[name] = m
        return m

    def create_threads(self):
        n_cells = self.n_cells
        bits = ceil(log2(n_cells))
        m_width = bits * 2
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
        done = m.Output("done")

        th = m.OutputReg("th", t_bits)
        v = m.OutputReg("v")
        cell1 = m.Output("cell1", bits)
        cell2 = m.Output("cell2", bits)

        m_rd = m.Reg("m_rd")
        m_rd_addr = m.Reg("m_rd_addr", t_bits)
        m_out1 = m.Wire("m_out1", m_width)
        m_wr = m.Reg("m_wr")
        m_wr_addr = m.Reg("m_wr_addr", t_bits)
        m_wr_data = m.Reg("m_wr_data", m_width)
        sum = m.Wire('sum', m_width)
        init_mem = m.Reg("init_mem", n_threads)
        done_mem = m.Reg("done_mem", t_bits)
        done.assign(Uand(done_mem))
        cell1.assign(m_out1[0: cell1.width])
        cell2.assign(m_out1[cell2.width: m_out1.width])
        sum.assign(Mux(init_mem[m_wr_addr], m_out1 + 1, 1))

        m.Always(Posedge(clk))(
            If(rst)(
                init_mem(0),
                m_rd_addr(0),
                done_mem(0),
                m_rd(0),
                v(0),
                th(0),
            ).Elif(start)(
                init_mem[m_rd_addr](1),
                m_rd(1),
                v(~done_mem[m_rd_addr]),
                th(m_rd_addr),
                If(m_rd_addr == n_threads - 1)(
                    m_rd_addr(0),
                ).Else(
                    m_rd_addr.inc(),
                )
            )
        )

        m.Always(Posedge(clk))(
            If(sum == n_cells-2)(
                done_mem[m_rd_addr](1)
            ),
            m_wr_addr(m_rd_addr),
            m_wr(m_rd),
            m_wr_data(sum)
        )

        par = []
        con = [
            ("clk", clk),
            ("rd", m_rd),
            ("rd_addr1", m_rd_addr),
            ("out_1", m_out1),
            ("wr", m_wr),
            ("wr_addr", m_wr_addr),
            ("wr_data", m_wr_data),
        ]
        aux = self.create_memory_2r_1w(m_width, t_bits)
        m.Instance(aux, aux.name, par, con)

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


#comp = SAComponents()
# comp.create_thread().to_verilog('thread.v')
# comp.create_arbiter().to_verilog('arbiter.v')
# comp.create_memory_2r_1w(32, 8).to_verilog('memory_2r_1w.v')
#comp.create_threads().to_verilog("threads.v")
