from math import ceil, log2, sqrt
from veriloggen import *
from src.utils import util


class SAComponents:
    _instance = None

    # def __new__(cls):
    #    if cls._instance is None:
    #        cls._instance = super().__new__(cls)
    #    return cls._instance

    def __init__(
        self,
        sa_graph: util.SaGraph,
        n_threads: int = 4,
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
        rd_addr0 = m.Input("rd_addr0", depth)
        rd_addr1 = m.Input("rd_addr1", depth)
        out0 = m.OutputReg("out0", width)
        out1 = m.OutputReg("out1", width)

        wr = m.Input("wr")
        wr_addr = m.Input("wr_addr", depth)
        wr_data = m.Input("wr_data", width)

        mem = m.Reg("mem", width, int(pow(2, depth)))

        m.Always(Posedge(clk))(
            If(rd)(out0(mem[rd_addr0]), out1(mem[rd_addr1])),
            If(wr)(mem[wr_addr](wr_data)),
        )

        m.EmbeddedCode('//synthesis translate_off')
        i = m.Integer('i')
        m.Initial(
            out0(0),
            out1(0),
            For(i(0), i < Power(2, depth), i.inc())(
                mem[i](0)
            ),
            Systask('readmemh', init_file, mem)
        )
        m.EmbeddedCode('//synthesis translate_on')
        self.cache[name] = m
        return m

    # FIXME - Change this component to run config times
    def create_threads_controller(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "threads_controller_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        par = []
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
        cell0 = m.OutputReg("cell0", c_bits)
        cell1 = m.OutputReg("cell1", c_bits)

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
                cell0(0),
                cell1(0),
            ).Else(
                If(p_rd)(
                    If(init_mem[p_addr])(
                        cell0(m_out[0:cell0.width]),
                        cell1(m_out[cell0.width:m_out.width]),
                        m_wr_data(m_out + 1),
                    ).Else(
                        init_mem[p_addr](1),
                        cell0(1),
                        cell1(0),
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

        con = [
            ("clk", clk),
            ("rd", m_rd),
            ("rd_addr0", m_rd_addr),
            ("out0", m_out),
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

        par = []
        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        m_depth = c_bits + t_bits
        node_bits = c_bits + 1
        m_width = node_bits

        m = Module(name)

        clk = m.Input('clk')

        # data to pass
        th_done_in = m.Input('th_done_in')
        th_v_in = m.Input('th_v_in')
        th_in = m.Input('th_in', t_bits)
        th_cell0_in = m.Input('th_cell0_in', c_bits)
        th_cell1_in = m.Input('th_cell1_in', c_bits)

        th_done_out = m.OutputReg('th_done_out')
        th_v_out = m.OutputReg('th_v_out')
        th_out = m.OutputReg('th_out', t_bits)
        th_cell0_out = m.OutputReg('th_cell0_out', c_bits)
        th_cell1_out = m.OutputReg('th_cell1_out', c_bits)

        th_ch_in = m.Input('th_ch_in', t_bits)
        flag_ch_in = m.Input('flag_ch_in')

        th_ch_out = m.Input('th_ch_out', t_bits)
        flag_ch_out = m.OutputReg('flag_ch_out')

        # data needed to exec
        node0 = m.Output('node0', node_bits)
        node1 = m.Output('node1', node_bits)

        m0_wr = m.Reg("m0_wr")
        m0_wr_addr = m.Reg("m0_wr_addr", m_depth)
        m0_wr_data = m.Reg("m0_wr_data", m_width)
        m0_out0 = m.Wire('m0_out0', m_width)
        m0_out1 = m.Wire('m0_out1', m_width)

        m.EmbeddedCode('')

        m1_wr = m.Reg("m1_wr")
        m1_wr_addr = m.Reg("m1_wr_addr", m_depth)
        m1_wr_data = m.Reg("m1_wr_data", m_width)
        m1_out0 = m.Wire('m1_out0', m_width)
        m1_out1 = m.Wire('m1_out1', m_width)

        m.EmbeddedCode('')

        p_wr = m.Reg("p_wr1")
        p_wr_addr = m.Reg("p_wr_addr1", m_depth)
        p_wr_data = m.Reg("p_wr_data")
        p_out0 = m.Wire('p_out0')
        p_out1 = m.Wire('p_out1')

        m.EmbeddedCode('')

        ch_wr = m.Reg('ch_wr')
        ch_wr_addr = m.Reg('ch_wr_addr', t_bits)
        ch_wr_data = m.Reg('ch_wr_data', (node_bits*2) + (c_bits*2) + 2)
        ch_out = m.Wire('ch_out', ch_wr_data.width)

        m.EmbeddedCode('')

        n0 = m.Wire('n0', node_bits)
        n1 = m.Wire('n1', node_bits)
        p0 = m.Wire('p0')
        p1 = m.Wire('p1')
        ch_cell0 = m.Wire('ch_cell0', c_bits)
        ch_cell1 = m.Wire('ch_cell1', c_bits)

        m.EmbeddedCode('')

        node0.assign(Mux(p_out0, m1_out0, m0_out0))
        node1.assign(Mux(p_out1, m1_out1, m0_out1))

        m.EmbeddedCode('')

        idx = 0
        p0.assign(ch_out[idx])
        idx += 1
        p1.assign(ch_out[idx])
        idx += 1
        n0.assign(ch_out[idx:idx+node_bits])
        idx += node_bits
        n1.assign(ch_out[idx:idx+node_bits])
        idx += node_bits
        ch_cell0.assign(ch_out[idx:idx+c_bits])
        idx += c_bits
        ch_cell1.assign(ch_out[idx:idx+c_bits])

        m.Always(Posedge(clk))(
            ch_wr(0),
            If(th_v_out)(
                ch_wr(1),
                ch_wr_addr(th_out),
                ch_wr_data(Cat(th_cell1_out, th_cell0_out,
                               node1, node0, p_out1, p_out0)),
            ),
            m0_wr(0),
            m1_wr(0),
            p_wr(0),
            If(flag_ch_out)(
                m0_wr(1),
                m1_wr(1),
                If(p0)(
                    m0_wr_addr(Cat(th_ch_out, ch_cell1)),
                    m0_wr_data(n0),

                    m1_wr_addr(Cat(th_ch_out, ch_cell0)),
                    m1_wr_data(n1),
                ).Else(
                    m0_wr_addr(Cat(th_ch_out, ch_cell0)),
                    m0_wr_data(n1),

                    m1_wr_addr(Cat(th_ch_out, ch_cell1)),
                    m1_wr_data(n0),
                ),
                If(Uxnor(Cat(p0, p1)))(
                    p_wr(1),
                    p_wr_addr(Cat(th_ch_out, ch_cell1)),
                    p_wr_data(~p1)
                ),
            )
        )

        # passing pipeline data
        m.Always(Posedge(clk))(
            th_done_out(th_done_in),
            th_v_out(th_v_in),
            th_out(th_in),
            th_cell0_out(th_cell0_in),
            th_cell1_out(th_cell1_in),
            th_ch_out(th_ch_in),
            flag_ch_out(flag_ch_in),
        )

        con = [
            ('clk', clk),
            ('rd', 1),
            ('rd_addr0', th_cell0_in),
            ('rd_addr1', th_cell1_in),
            ('out0', m0_out0),
            ('out1', m0_out1),
            ('wr', m0_wr),
            ('wr_addr', m0_wr_addr),
            ('wr_data', m0_wr_data)
        ]

        aux = self.create_memory_2r_1w(m_width, m_depth)
        m.Instance(aux, 'm0_' + aux.name, par, con)

        con = [
            ('clk', clk),
            ('rd', 1),
            ('rd_addr0', th_cell0_in),
            ('rd_addr1', th_cell1_in),
            ('out0', m1_out0),
            ('out1', m1_out1),
            ('wr', m1_wr),
            ('wr_addr', m1_wr_addr),
            ('wr_data', m1_wr_data)
        ]

        aux = self.create_memory_2r_1w(m_width, m_depth)
        m.Instance(aux, 'm1_' + aux.name, par, con)

        con = [
            ('clk', clk),
            ('rd', 1),
            ('rd_addr0', th_cell0_in),
            ('rd_addr1', th_cell1_in),
            ('out0', p_out0),
            ('out1', p_out1),
            ('wr', p_wr),
            ('wr_addr', p_wr_addr),
            ('wr_data', p_wr_data)
        ]

        aux = self.create_memory_2r_1w(1, m_depth)
        m.Instance(aux, 'p_' + aux.name, par, con)

        con = [
            ('clk', clk),
            ('rd', 1),
            ('rd_addr0', th_ch_in),
            ('out0', ch_out),
            ('wr', ch_wr),
            ('wr_addr', ch_wr_addr),
            ('wr_data', ch_wr_data)
        ]
        aux = self.create_memory_2r_1w(ch_wr_data.width, t_bits)
        m.Instance(aux, 'ch_' + aux.name, par, con)

        util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_neighbors_pipe(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "neighbors_pipe_%dcells_%dneighbors" % (n_cells, n_neighbors)
        if name in self.cache.keys():
            return self.cache[name]

        par = []
        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        m_depth = c_bits
        node_bits = c_bits + 1
        m_width = node_bits

        m = Module(name)

        clk = m.Input('clk')

        # data to pass
        th_done_in = m.Input('th_done_in')
        th_v_in = m.Input('th_v_in')
        th_in = m.Input('th_in', t_bits)
        th_cell0_in = m.Input('th_cell0_in', c_bits)
        th_cell1_in = m.Input('th_cell1_in', c_bits)
        th_node0_in = m.Input('th_node0_in', node_bits)
        th_node1_in = m.Input('th_node1_in', node_bits)

        th_done_out = m.OutputReg('th_done_out')
        th_v_out = m.OutputReg('th_v_out')
        th_out = m.OutputReg('th_out', t_bits)
        th_cell0_out = m.OutputReg('th_cell0_out', c_bits)
        th_cell1_out = m.OutputReg('th_cell1_out', c_bits)
        th_node0_out = m.OutputReg('th_node0_out', node_bits)
        th_node1_out = m.OutputReg('th_node1_out', node_bits)

        th_ch_in = m.Input('th_ch_in', t_bits)
        flag_ch_in = m.Input('flag_ch_in')

        th_ch_out = m.Input('th_ch_out', t_bits)
        flag_ch_out = m.OutputReg('flag_ch_out')

        # data needed to exec
        neighbor = m.Output('neighbor', node_bits)

        m_out0 = m.Wire('m_out0', node_bits)
        m.EmbeddedCode('')
        neighbor.assign(Mux(th_node0_out[th_node0_out.width], m_out0, 0))

        # passing pipeline data
        m.Always(Posedge(clk))(
            th_done_out(th_done_in),
            th_v_out(th_v_in),
            th_out(th_in),
            th_cell0_out(th_cell0_in),
            th_cell1_out(th_cell1_in),
            th_ch_out(th_ch_in),
            flag_ch_out(flag_ch_in),
            th_node0_out(th_node0_in),
            th_node1_out(th_node1_in)
        )

        con = [
            ('clk', clk),
            ('rd', 1),
            ('rd_addr0', th_node0_in[0:c_bits]),
            ('out0', m_out0),
            ('wr', 0),
            ('wr_addr', 0),
            ('wr_data', 0)
        ]
        aux = self.create_memory_2r_1w(node_bits, m_depth)
        m.Instance(aux, 'm_' + aux.name, par, con)

        util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_node_cell_pipe(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "node_cell_pipe_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        par = []
        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        m_depth = c_bits + t_bits
        node_bits = c_bits + 1
        #m_width = c_bits

        m = Module(name)

        clk = m.Input('clk')

        # data to pass
        th_done_in = m.Input('th_done_in')
        th_v_in = m.Input('th_v_in')
        th_in = m.Input('th_in', t_bits)
        th_cell0_in = m.Input('th_cell0_in', c_bits)
        th_cell1_in = m.Input('th_cell1_in', c_bits)
        th_node0_in = m.Input('th_node0_in', node_bits)
        th_node1_in = m.Input('th_node1_in', node_bits)

        th_cell0_out = m.OutputReg('th_cell0_out', c_bits)
        th_cell1_out = m.OutputReg('th_cell1_out', c_bits)

        th_ch_in = m.Input('th_ch_in', t_bits)
        flag_ch_in = m.Input('flag_ch_in')

        th_neighbor_in = m.Input('th_neighbor_in', node_bits)

        # data needed to exec
        node0_v = m.Output('node0_v')
        neighbor_cell = m.Output('neighbor_cell', node_bits)

        m0_wr = m.Reg("m0_wr")
        m0_wr_addr = m.Reg("m0_wr_addr", m_depth)
        m0_wr_data = m.Reg("m0_wr_data", c_bits)
        m0_out0 = m.Wire('m0_out0', c_bits)

        m.EmbeddedCode('')

        m1_wr = m.Reg("m1_wr")
        m1_wr_addr = m.Reg("m1_wr_addr", m_depth)
        m1_wr_data = m.Reg("m1_wr_data", c_bits)
        m1_out0 = m.Wire('m1_out0', c_bits)

        m.EmbeddedCode('')

        p_wr = m.Reg("p_wr1")
        p_wr_addr = m.Reg("p_wr_addr1", m_depth)
        p_wr_data = m.Reg("p_wr_data")
        p_out0 = m.Wire('p_out0')
        p_out1 = m.Wire('p_out1')

        m.EmbeddedCode('')

        ch_wr = m.Reg('ch_wr')
        ch_wr_addr = m.Reg('ch_wr_addr', t_bits)
        ch_wr_data = m.Reg('ch_wr_data', (node_bits*2) + (c_bits*2) + 2)
        ch_out = m.Wire('ch_out', ch_wr_data.width)

        m.EmbeddedCode('')

        n0 = m.Wire('n0', c_bits)
        n0_v = m.Wire('n0_v')
        n1 = m.Wire('n1', c_bits)
        n1_v = m.Wire('n1_v')
        p0 = m.Wire('p0')
        p1 = m.Wire('p1')
        ch_cell0 = m.Wire('ch_cell0', c_bits)
        ch_cell1 = m.Wire('ch_cell1', c_bits)

        m.EmbeddedCode('')

        idx = 0
        p0.assign(ch_out[idx])
        idx += 1
        p1.assign(ch_out[idx])
        idx += 1
        n0.assign(ch_out[idx:idx+c_bits])
        idx += c_bits
        n0_v.assign(ch_out[idx])
        idx += 1
        n1.assign(ch_out[idx:idx+c_bits])
        idx += c_bits
        n1_v.assign(ch_out[idx])
        idx += 1
        ch_cell0.assign(ch_out[idx:idx+c_bits])
        idx += c_bits
        ch_cell1.assign(ch_out[idx:idx+c_bits])

        m.EmbeddedCode('')
        flag_ch_p = m.Reg('flag_ch_p')
        th_ch_p = m.Reg('th_ch_p', t_bits)
        n0_v_p = m.Reg('n0_v_p')
        neighbor_v_p = m.Reg('neighbor_v_p')

        m.EmbeddedCode('')

        neighbor_cell[neighbor_cell.width-1].assign(neighbor_v_p)
        neighbor_cell[:c_bits].assign(Mux(p_out0, m1_out0, m0_out0))
        node0_v.assign(n0_v)

        m.Always(Posedge(clk))(
            flag_ch_p(flag_ch_in),
            th_ch_p(th_in),
            n0_v_p(th_node0_in[th_node0_in.width-1]),
            neighbor_v_p(th_neighbor_in[th_neighbor_in.width-1])
        )

        m.Always(Posedge(clk))(
            ch_wr(0),
            If(th_v_in)(
                ch_wr(1),
                ch_wr_addr(th_in),
                ch_wr_data(Cat(th_cell1_in, th_cell0_in,
                               th_node1_in, th_node0_in, p_out1, p_out0)),
            ),
            m0_wr(0),
            m1_wr(0),
            p_wr(0),
            If(flag_ch_p)(
                If(p0)(
                    m0_wr(n1_v),
                    m1_wr(n0_v),

                    m0_wr_addr(Cat(th_ch_p, n1)),
                    m0_wr_data(ch_cell0),

                    m1_wr_addr(Cat(th_ch_p, n0)),
                    m1_wr_data(ch_cell1),
                ).Else(
                    m0_wr(n0_v),
                    m1_wr(n1_v),

                    m0_wr_addr(Cat(th_ch_p, n0)),
                    m0_wr_data(ch_cell1),

                    m1_wr_addr(Cat(th_ch_p, n1)),
                    m1_wr_data(ch_cell0),
                ),
                If(Uxnor(Cat(p0, p1)))(
                    p_wr(n1_v),
                    p_wr_addr(Cat(th_ch_p, n1)),
                    p_wr_data(~p1)
                ),
            )
        )

        # passing pipeline data
        m.Always(Posedge(clk))(
            th_cell0_out(th_cell0_in),
            th_cell1_out(th_cell1_in),
        )

        con = [
            ('clk', clk),
            ('rd', 1),
            ('rd_addr0', th_neighbor_in[:th_neighbor_in.width-1]),
            ('out0', m0_out0),
            ('wr', m0_wr),
            ('wr_addr', m0_wr_addr),
            ('wr_data', m0_wr_data)
        ]

        aux = self.create_memory_2r_1w(c_bits, m_depth)
        m.Instance(aux, 'm0_' + aux.name, par, con)

        con = [
            ('clk', clk),
            ('rd', 1),
            ('rd_addr0', th_neighbor_in[:th_neighbor_in.width-1]),
            ('out0', m1_out0),
            ('wr', m1_wr),
            ('wr_addr', m1_wr_addr),
            ('wr_data', m1_wr_data)
        ]

        aux = self.create_memory_2r_1w(c_bits, m_depth)
        m.Instance(aux, 'm1_' + aux.name, par, con)

        con = [
            ('clk', clk),
            ('rd', 1),
            ('rd_addr0', th_neighbor_in[:th_neighbor_in.width-1]),
            ('out0', p_out0),
            ('wr', p_wr),
            ('wr_addr', p_wr_addr),
            ('wr_data', p_wr_data)
        ]

        aux = self.create_memory_2r_1w(1, m_depth)
        m.Instance(aux, 'p_' + aux.name, par, con)

        con = [
            ('clk', clk),
            ('rd', 1),
            ('rd_addr0', th_ch_in),
            ('out0', ch_out),
            ('wr', ch_wr),
            ('wr_addr', ch_wr_addr),
            ('wr_data', ch_wr_data)
        ]
        aux = self.create_memory_2r_1w(ch_wr_data.width, t_bits)
        m.Instance(aux, 'ch_' + aux.name, par, con)

        util.initialize_regs(m)
        self.cache[name] = m
        return m

    # TODO need to be developed
    def create_cell_selector(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'cell_selector'
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits + 1

        m = Module(name)

        th_cell0_in = m.Input('th_cell0_in', c_bits)
        th_cell1_in = m.Input('th_cell1_in', c_bits)
        th_node0_v_in = m.Input('th_node0_v_in')
        th_neighbor_cell_in = m.Input('neighbor_cell_in', node_bits)
        opb0 = m.Output('opb0', c_bits)
        opb1 = m.Output('opb1', c_bits)
        opa0 = m.Output('opa0', c_bits)
        opa1 = m.Output('opa1', c_bits)
        v = m.Output('v')
        neighbor_v = m.Wire('neighbor_v')
        neighbor_cell = m.Wire('neighbor_cell', c_bits)

        neighbor_v.assign(th_neighbor_cell_in[th_neighbor_cell_in.width-1])
        neighbor_cell.assign(th_neighbor_cell_in[:th_neighbor_cell_in.width-1])

        m.EmbeddedCode('')

        v.assign(Uand(Cat(th_node0_v_in, neighbor_v)))

        m.EmbeddedCode('')

        opb0.assign(th_cell0_in)
        opb1.assign(neighbor_cell)

        opa0.assign(th_cell1_in)
        opa1.assign(Mux(neighbor_cell == th_cell1_in, th_cell0_in, neighbor_cell))
        

        # opa0.assign()
        # opa1.assign()
        # opb0.assign()
        # opb1.assign()
        util.initialize_regs(m)
        self.cache[name] = m
        return m

    # TODO need to be developed
    def create_distance_rom(self):
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads
        lines = columns = int(sqrt(n_cells))

        name = 'distance_rom_%d_%d' % (lines, columns)
        if name in self.cache.keys():
            return self.cache[name]

        par = []
        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits + 1

        # shortest Manhattan distance
        d_width = ceil(log2(lines+columns))
        d_width += ceil(log2(n_neighbors))

        m = Module(name)

        clk = m.Input('clk')
        opb0 = m.Input('opb0', c_bits)
        opb1 = m.Input('opb1', c_bits)
        opa0 = m.Input('opa0', c_bits)
        opa1 = m.Input('opa1', c_bits)
        d0 = m.Output('d0', d_width)
        d1 = m.Output('d1', d_width)

        '''
        mem = m.Wire('mem', d0.width, lines * columns)

        m.Always(Posedge(clk))(
            If(re)(
                d0(mem[cell0]),
                d1(mem[cell1]),
            )
        )

        line_counter = 0
        for l in distance_matrix:
            s = "{"
            for c in l:
                s = s + str(c) + ","
            s = s[:-1]
            s = s + "}"
            mem[line_counter].assign(EmbeddedCode(s))
            line_counter = line_counter + 1
        '''
        util.initialize_regs(m)
        self.cache[name] = m
        return m

    # TODO need to be developed
    def create_cell0_exec_pipe(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "cell0_exec_%dthreads_%dcells_%dneighbors" % (
            n_threads, n_cells, n_neighbors)
        if name in self.cache.keys():
            return self.cache[name]

        par = []
        con = []
        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits + 1
        lines = columns = int(sqrt(n_cells))
        # shortest Manhattan distance
        d_width = ceil(log2(lines+columns))
        d_width += ceil(log2(n_neighbors))

        m = Module(name)
        clk = m.Input('clk')

        # data to pass
        th_done_in = m.Input('th_done_in')
        th_v_in = m.Input('th_v_in')
        th_in = m.Input('th_in', t_bits)
        th_cell0_in = m.Input('th_cell0_in', c_bits)
        th_cell1_in = m.Input('th_cell1_in', c_bits)

        cn_th_done_out = m.Wire('cn_th_done_out')
        cn_th_v_out = m.Wire('cn_th_v_out')
        cn_th_out = m.Wire('cn_th_out', t_bits)
        cn_th_cell0_out = m.Wire('cn_th_cell0_out', c_bits)
        cn_th_cell1_out = m.Wire('cn_th_cell1_out', c_bits)
        cn_th_ch_in = m.Wire('cn_th_ch_in', t_bits)
        cn_flag_ch_in = m.Wire('cn_flag_ch_in')
        cn_th_ch_out = m.Wire('cn_th_ch_out', t_bits)
        cn_flag_ch_out = m.Wire('cn_flag_ch_out')
        cn_node0 = m.Wire('cn_node0', node_bits)
        cn_node1 = m.Wire('cn_node1', node_bits)

        con = []
        con.append(('clk', clk))
        con.append(('th_done_in', th_done_in))
        con.append(('th_v_in', th_v_in))
        con.append(('th_in', th_in))
        con.append(('th_cell0_in', th_cell0_in))
        con.append(('th_cell1_in', th_cell1_in))
        con.append(('th_done_out', cn_th_done_out))
        con.append(('th_v_out', cn_th_v_out))
        con.append(('th_out', cn_th_out))
        con.append(('th_cell0_out', cn_th_cell0_out))
        con.append(('th_cell1_out', cn_th_cell1_out))
        con.append(('th_ch_in', cn_th_ch_in))
        con.append(('flag_ch_in', cn_flag_ch_in))
        con.append(('th_ch_out', cn_th_ch_out))
        con.append(('flag_ch_out', cn_flag_ch_out))
        con.append(('node0', cn_node0))
        con.append(('node1', cn_node1))

        aux = self.create_cell_node_pipe()
        m.Instance(aux, 'cn0_'+aux.name, par, con)

        n_th_done_out = m.Wire('n_th_done_out', n_neighbors)
        n_th_v_out = m.Wire('n_th_v_out', n_neighbors)
        n_th_out = m.Wire('n_th_out', t_bits, n_neighbors)
        n_th_cell0_out = m.Wire('n_th_cell0_out', c_bits, n_neighbors)
        n_th_cell1_out = m.Wire('n_th_cell1_out', c_bits, n_neighbors)
        n_th_node0_out = m.Wire('n_th_node0_out', node_bits, n_neighbors)
        n_th_node1_out = m.Wire('n_th_node1_out', node_bits, n_neighbors)
        n_th_ch_out = m.Wire('n_th_ch_out', t_bits, n_neighbors)
        n_flag_ch_out = m.Wire('n_flag_ch_out', n_neighbors)
        n_neighbor = m.Wire('n_neighbor', node_bits, n_neighbors)

        m.EmbeddedCode('')

        nc_th_cell0_out = m.Wire('nc_th_cell0_out', c_bits, n_neighbors)
        nc_th_cell1_out = m.Wire('nc_th_cell1_out', c_bits, n_neighbors)
        nc_node0_v = m.Wire('nc_node0_v', n_neighbors)
        nc_neighbor_cell = m.Wire('nc_neighbor_cell', node_bits, n_neighbors)

        m.EmbeddedCode('')

        cs_opa0 = m.Wire('cs_opa0', c_bits, n_neighbors)
        cs_opa1 = m.Wire('cs_opa1', c_bits, n_neighbors)
        cs_opb0 = m.Wire('cs_opb0', c_bits, n_neighbors)
        cs_opb1 = m.Wire('cs_opb1', c_bits, n_neighbors)

        m.EmbeddedCode('')

        dm_d0 = m.Wire('dm_d0', d_width, n_neighbors)
        dm_d1 = m.Wire('dm_d1', d_width, n_neighbors)

        for i in range(n_neighbors):
            m.EmbeddedCode('// Pipe neighbor %d' % i)
            con = []
            con.append(('clk', clk))
            if i == 0:
                con.append(('th_done_in', cn_th_done_out))
                con.append(('th_v_in', cn_th_v_out))
                con.append(('th_in', cn_th_out))
                con.append(('th_cell0_in', cn_th_cell0_out))
                con.append(('th_cell1_in', cn_th_cell1_out))
                con.append(('th_node0_in', cn_node0))
                con.append(('th_node1_in', cn_node1))
                con.append(('th_ch_in', cn_th_ch_out))
                con.append(('flag_ch_in', cn_flag_ch_out))
            else:
                con.append(('th_done_in', n_th_done_out[i-1]))
                con.append(('th_v_in', n_th_v_out[i-1]))
                con.append(('th_in', n_th_out[i-1]))
                con.append(('th_cell0_in', n_th_cell0_out[i-1]))
                con.append(('th_cell1_in', n_th_cell1_out[i-1]))
                con.append(('th_node0_in', n_th_node1_out[i-1]))
                con.append(('th_node1_in', n_th_node1_out[i-1]))
                con.append(('th_ch_in', n_th_ch_out[i-1]))
                con.append(('flag_ch_in', n_flag_ch_out[i-1]))
            con.append(('th_done_out', n_th_done_out[i]))
            con.append(('th_v_out', n_th_v_out[i]))
            con.append(('th_out', n_th_out[i]))
            con.append(('th_cell0_out', n_th_cell0_out[i]))
            con.append(('th_cell1_out', n_th_cell1_out[i]))
            con.append(('th_node0_out', n_th_node0_out[i]))
            con.append(('th_node1_out', n_th_node1_out[i]))
            con.append(('th_ch_out', n_th_ch_out[i]))
            con.append(('flag_ch_out', n_flag_ch_out[i]))
            con.append(('neighbor', n_neighbor[i]))

            aux = self.create_neighbors_pipe()
            m.Instance(aux, '%s_%d' % (aux.name, i), par, con)

            con = []
            con.append(('clk', clk))
            con.append(('th_done_in', n_th_done_out[i]))
            con.append(('th_v_in', n_th_v_out[i]))
            con.append(('th_in', n_th_out[i]))
            con.append(('th_cell0_in', n_th_cell0_out[i]))
            con.append(('th_cell1_in', n_th_cell1_out[i]))
            con.append(('th_node0_in', n_th_node0_out[i]))
            con.append(('th_node1_in', n_th_node1_out[i]))
            con.append(('th_ch_in', n_th_ch_out[i]))
            con.append(('flag_ch_in', n_flag_ch_out[i]))
            con.append(('th_cell0_out', nc_th_cell0_out[i]))
            con.append(('th_cell1_out', nc_th_cell1_out[i]))
            con.append(('node0_v', nc_node0_v[i]))
            con.append(('neighbor_cell', nc_neighbor_cell[i]))

            aux = self.create_node_cell_pipe()
            m.Instance(aux, '%s_%d' % (aux.name, i), par, con)

            con = []
            con.append(('th_cell0_in', nc_th_cell0_out[i]))
            con.append(('th_cell1_in', nc_th_cell1_out[i]))
            con.append(('th_node0_v_in', nc_node0_v[i]))
            con.append(('neighbor_cell_in', nc_neighbor_cell[i]))
            con.append(('opb0', cs_opb0[i]))
            con.append(('opb1', cs_opb1[i]))
            con.append(('opa0', cs_opa0[i]))
            con.append(('opa1', cs_opa1[i]))

            aux = self.create_cell_selector()
            m.Instance(aux, '%s_%d' % (aux.name, i), par, con)

            con = []
            con.append(('clk', clk))
            con.append(('opb0', cs_opb0[i]))
            con.append(('opb1', cs_opb1[i]))
            con.append(('opa0', cs_opa0[i]))
            con.append(('opa1', cs_opa1[i]))
            con.append(('d0', dm_d0[i]))
            con.append(('d1', dm_d1[i]))

            aux = self.create_distance_rom()
            m.Instance(aux, '%s_%d' % (aux.name, i), par, con)

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

        par = []
        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits + 1

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

        # FIXME - Change this component to run config times
        th_done = m.Wire('th_done')
        th_v = m.Wire('th_v')
        th = m.Wire('th', t_bits)
        th_cell0 = m.Wire('th_cell0', c_bits)
        th_cell1 = m.Wire('th_cell1', c_bits)
        par = []
        con = [
            ('clk', clk),
            ('rst', rst),
            ('start', start),
            ('done', th_done),
            ('v', th_v),
            ('th', th),
            ('cell0', th_cell0),
            ('cell1', th_cell1),
        ]
        aux = self.create_threads_controller()
        m.Instance(aux, aux.name, par, con)

        con = [
            ('clk', clk),
            ('th_done_in', th_done),
            ('th_v_in', th_v),
            ('th_in', th),
            ('th_cell0_in', th_cell0),
            ('th_cell1_in', th_cell1),
        ]
        aux = self.create_cell0_exec_pipe()
        m.Instance(aux, aux.name, par, con)
        util.initialize_regs(m)
        return m
