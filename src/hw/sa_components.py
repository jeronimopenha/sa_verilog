from math import ceil, log2, sqrt
from veriloggen import *
from src.utils import util


class SAComponents:
    _instance = None

    #def __new__(cls):
    #    if cls._instance is None:
    #        cls._instance = super().__new__(cls)
    #    return cls._instance

    def __init__(
        self,
        sa_graph: util.SaGraph,
        n_threads: int = 1,
        n_neighbors: int = 4,
        align_bits: int = 8,
    ):
        self.sa_graph = sa_graph
        self.n_cells = sa_graph.n_cells
        self.n_neighbors = n_neighbors
        self.align_bits = align_bits
        self.n_threads = n_threads
        self.cache = {}

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

    #FIXME - Change this component to run config times
    def create_threads_controller(self) -> Module:
        sa_graph = sa_graph
        n_cells = sa_graph.n_cells
        n_neighbors = n_neighbors
        align_bits = align_bits
        n_threads = n_threads

        name = "threads_controller_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        m_width = c_bits * 2
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits

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

        util.initialize_regs(m)

        self.cache[name] = m
        return m

    def create_cell_node_pipe(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads
        
        name = "cell_node_pipe_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        m_depth = c_bits + t_bits
        node_width = c_bits + 1

        m = Module(name)

        clk = m.Input('clk')

        #data to pass
        th_done_in = m.Input('th_done_in')
        th_v_in = m.Input('th_v_in')
        th_in = m.Input('th_in', t_bits)
        th_cell1_in = m.Input('th_cell1_in', c_bits)
        th_cell2_in = m.Input('th_cell2_in', c_bits)
        
        th_done_out = m.OutputReg('th_done_out')
        th_v_out = m.OutputReg('th_v_out')
        th_out = m.OutputReg('th_out', t_bits)
        th_cell1_out = m.OutputReg('th_cell1_out', c_bits)
        th_cell2_out = m.OutputReg('th_cell2_out', c_bits)

        #data needed to exec
        cell_wr = m.Input("cell_wr")
        cell_wr_addr = m.Input("cell_wr_addr", m_depth)
        cell_wr_node = m.Input("cell_wr_node", node_width)

        node = m.Output('node', node_width)
        
        #passing pipeline data
        m.Always(Posedge(clk))(
            th_done_out(th_done_in),
            th_v_out(th_v_in),
            th_out(th_in),
            th_cell1_out(th_cell1_in),
            th_cell2_out(th_cell2_in),            
        )

        par = []
        con = [
            ('clk', clk),
            ('rd', 1),
            ('rd_addr1', th_cell1_in),
            ('out1', node),
            ('wr', cell_wr),
            ('wr_addr', cell_wr_addr),
            ('wr_data', cell_wr_node)
        ]
        aux = self.create_memory_2r_1w(node_width, m_depth)
        m.Instance(aux, aux.name, par, con)

        util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_cell_exec_pipe(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "cell_exec_%dthreads_%dcells_%dneighbors" % (n_threads, n_cells, n_neighbors)
        if name in self.cache.keys():
            return self.cache[name]
        
        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits

        m = Module(name)
        clk = m.Input('clk')
        rst = m.Input('rst')

        #data to pass
        th_done_in = m.Input('th_done_in')
        th_v_in = m.Input('th_v_in')
        th_in = m.Input('th_in', t_bits)
        th_cell1_in = m.Input('th_cell1_in', c_bits)
        th_cell2_in = m.Input('th_cell2_in', c_bits)
        
        th_done_out = m.Output('th_done_out')
        th_v_out = m.Output('th_v_out')
        th_out = m.Output('th_out', t_bits)
        th_cell1_out = m.Output('th_cell1_out', c_bits)
        th_cell2_out = m.Output('th_cell2_out', c_bits)

        #data to send

        m.Always(Posedge(clk))(
            th_done_out(th_done_in),
            th_v_out(th_v_in),
            th_out(th_in),
            th_cell1_out(th_cell1_in),
            th_cell2_out(th_cell2_in),            
        )

        util.initialize_regs(m)
        return m

    def create_sa(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "sa_%dthreads_%dcells_%dneighbors" % (
            n_threads, n_cells, n_neighbors)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits

        m = Module(name)

        clk = m.Input('clk')
        rst = m.Input('rst')

        # TODO
        start = m.Reg('start')

        m.Always(Posedge(clk))(
            If(rst)(
                start(0),
            ).Else(
                start(1),
            )
        )

        #FIXME - Change this component to run config times
        th_done = m.Wire('th_done')
        th_v = m.Wire('th_v')
        th = m.Wire('th', t_bits)
        th_cell1 = m.Wire('th_cell1', c_bits)
        th_cell2 = m.Wire('th_cell2', c_bits)
        par = []
        con = [
            ('clk', clk),
            ('rst', rst),
            ('start', start),
            ('done', th_done),
            ('v', th_v),
            ('th', th),
            ('cell1', th_cell1),
            ('cell2', th_cell2),
        ]
        aux = self.create_threads_controller()
        m.Instance(aux, aux.name, par, con)

        cnmp_cell1 = m.Wire('cnmp_cell1', c_bits)
        cnmp_cell2 = m.Wire('cnmp_cell2', c_bits)
        cnmp_v = m.Wire('cnmp_v')
        cnmp_node1 = m.Wire('cnmp_node1', m_width)
        cnmp_node2 = m.Wire('cnmp_node2', m_width)
        cnmp_wr = m.Wire('cnmp_wr',)
        cnmp_wr_addr = m.Wire('cnmp_wr_addr', m_depth)
        cnmp_wr_data = m.Wire('cnmp_wr_data', m_depth)

        # TODO
        cnmp_wr.assign(0)
        cnmp_wr_addr.assign(0)
        cnmp_wr_data.assign(0)

        par = []
        con = [
            ('clk', clk),
            ('cell1_i', th_cell1),
            ('cell2_i', th_cell2),
            ('v_i', th_v),
            ('cell1_o', cnmp_cell1),
            ('cell1_o', cnmp_cell2),
            ('v_o', cnmp_v),
            ('node1', cnmp_node1),
            ('node2', cnmp_node2),
            ('wr', cnmp_wr),
            ('wr_addr', cnmp_wr_addr),
            ('wr_data', cnmp_wr_data)
        ]
        aux = self.create_cell_node_pipe()
        m.Instance(aux, aux.name, par, con)
        util.initialize_regs(m)
        return m

