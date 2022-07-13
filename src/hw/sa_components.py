from functools import cache
import os
from math import ceil, dist, log2, sqrt
from veriloggen import *
from src.utils.util import initialize_regs, SaGraph


class SAComponents:
    _instance = None

    def __init__(
        self,
        sa_graph: SaGraph,
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

    def create_distance_rom(self) -> Module:
        # manhattan
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads
        lines = columns = int(sqrt(n_cells))

        name = 'distance_rom_%d_%d' % (lines, columns)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)

        opa0 = m.Input('opa0', c_bits)
        opa1 = m.Input('opa1', c_bits)
        opav = m.Input('opav')
        opb0 = m.Input('opb0', c_bits)
        opb1 = m.Input('opb1', c_bits)
        opbv = m.Input('opbv')
        da = m.Output('da', dist_bits)
        db = m.Output('db', dist_bits)

        mem = m.Wire('mem', dist_bits, Power(n_cells, 2))

        da.assign(Mux(opav, mem[Cat(opa1, opa0)], 0))
        db.assign(Mux(opbv, mem[Cat(opb1, opb0)], 0))

        r = int(sqrt(int(n_cells)))
        c = 0
        for x1 in range(r):
            for y1 in range(r):
                for x2 in range(r):
                    for y2 in range(r):
                        d = abs(y1-y2) + abs(x1-x2)
                        mem[c].assign(Int(d, dist_bits, 10))
                        c = c + 1

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st1_c2n(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "st1_c2n_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        ca_in = m.Input('ca_in', c_bits)
        cb_in = m.Input('cb_in', c_bits)
        sw_in = m.Input('sw_in')
        st1_wb_in = m.Input('st1_wb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        ca_out = m.OutputReg('ca_out', c_bits)
        cb_out = m.OutputReg('cb_out', c_bits)
        na_out = m.OutputReg('na_out', node_bits)
        na_v_out = m.OutputReg('na_v_out')
        nb_out = m.OutputReg('nb_out', node_bits)
        nb_v_out = m.OutputReg('nb_v_out')
        sw_out = m.OutputReg('sw_out')
        wa_out = m.OutputReg('wa_out', w_bits)
        wb_out = m.OutputReg('wb_out', w_bits)
        # -----

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st2_n(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "st2_n_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        ca_in = m.Input('ca_in', c_bits)
        cb_in = m.Input('cb_in', c_bits)
        na_in = m.Input('na_in', node_bits)
        na_v_in = m.Input('na_v_in')
        nb_in = m.Input('nb_in', node_bits)
        nb_v_in = m.Input('nb_v_in')
        sw_in = m.Input('sw_in')
        wa_in = m.Input('wa_in', w_bits)
        wb_in = m.Input('wb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        ca_out = m.OutputReg('ca_out', c_bits)
        cb_out = m.OutputReg('cb_out', c_bits)
        na_out = m.OutputReg('na_out', node_bits)
        na_v_out = m.OutputReg('na_v_out')
        nb_out = m.OutputReg('nb_out', node_bits)
        nb_v_out = m.OutputReg('nb_v_out')
        va_out = m.OutputReg('va_out', node_bits*n_neighbors)
        va_v_out = m.OutputReg('va_v_out', n_neighbors)
        vb_out = m.OutputReg('vb_out', node_bits*n_neighbors)
        vb_v_out = m.OutputReg('vb_v_out', n_neighbors)
        sw_out = m.OutputReg('sw_out')
        wa_out = m.OutputReg('wa_out', w_bits)
        wb_out = m.OutputReg('wb_out', w_bits)

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st3_n2c(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "st3_n2c_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        ca_in = m.Input('ca_in', c_bits)
        cb_in = m.Input('cb_in', c_bits)
        na_in = m.Input('na_in', node_bits)
        na_v_in = m.Input('na_v_in')
        nb_in = m.Input('nb_in', node_bits)
        nb_v_in = m.Input('nb_v_in')
        va_in = m.Input('va_in', node_bits*n_neighbors)
        va_v_in = m.Input('va_v_in', n_neighbors)
        vb_in = m.Input('vb_in', node_bits*n_neighbors)
        vb_v_in = m.Input('vb_v_in', n_neighbors)
        st3_wb_in = m.Input('st3_wb_in', w_bits)
        sw_in = m.Input('sw_in')
        wa_in = m.Input('wa_in', w_bits)
        wb_in = m.Input('wb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        ca_out = m.OutputReg('ca_out', c_bits)
        cb_out = m.OutputReg('cb_out', c_bits)
        cva_out = m.OutputReg('cva_out', c_bits*n_neighbors)
        cva_v_out = m.OutputReg('cva_v_out', n_neighbors)
        cvb_out = m.OutputReg('cvb_out', c_bits*n_neighbors)
        cvb_v_out = m.OutputReg('cvb_v_out', n_neighbors)
        wb_out = m.OutputReg('wb_out', w_bits)

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st4_d1(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "st4_d1_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        ca_in = m.Input('ca_in', c_bits)
        cb_in = m.Input('cb_in', c_bits)
        cva_in = m.Input('cva_in', c_bits*n_neighbors)
        cva_v_in = m.Input('cva_v_in', n_neighbors)
        cvb_in = m.Input('cvb_in', c_bits*n_neighbors)
        cvb_v_in = m.Input('cvb_v_in', n_neighbors)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        ca_out = m.OutputReg('ca_out', c_bits)
        cb_out = m.OutputReg('cb_out', c_bits)
        cva_out = m.OutputReg('cva_out', c_bits*n_neighbors)
        cva_v_out = m.OutputReg('cva_v_out', n_neighbors)
        cvb_out = m.OutputReg('cvb_out', c_bits*n_neighbors)
        cvb_v_out = m.OutputReg('cvb_v_out', n_neighbors)
        dvac_out = m.OutputReg('dvac_out', n_neighbors*dist_bits)
        dvbc_out = m.OutputReg('dvbc_out', n_neighbors*dist_bits)
        # -----

        cac = m.Wire('cac', c_bits)
        cbc = m.Wire('cbc', c_bits)
        dvac_t = m.Wire('dvac_t', n_neighbors*dist_bits)
        dvbc_t = m.Wire('dvbc_t', n_neighbors*dist_bits)

        cac.assign(ca_in)
        cbc.assign(cb_in)

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            ca_out(ca_in),
            cb_out(cb_in),
            cva_out(cva_in),
            cva_v_out(cva_v_in),
            cvb_out(cvb_in),
            cvb_v_out(cvb_v_in),
            dvac_out(dvac_t),
            dvbc_out(dvbc_t),
        )

        for i in range(0, (n_neighbors//2)+1, 2):
            par = []
            con = [
                ('opa0', cac),
                ('opa1', cva_in[i*c_bits:c_bits*(i+1)]),
                ('opav', cva_v_in[i]),
                ('opb0', cac),
                ('opb1', cva_in[c_bits*(i+1):c_bits*(i+2)]),
                ('opbv', cva_v_in[i+1]),
                ('da', dvac_t[i*dist_bits:dist_bits*(i+1)]),
                ('db', dvac_t[dist_bits*(i+1):dist_bits*(i+2)]),
            ]
            aux = self.create_distance_rom()
            m.Instance(aux, '%s_dac_%d' % (aux.name, (i // 2)), par, con)

        for i in range(0, (n_neighbors//2)+1, 2):
            par = []
            con = [
                ('opa0', cbc),
                ('opa1', cvb_in[i*c_bits:c_bits*(i+1)]),
                ('opav', cvb_v_in[i]),
                ('opb0', cbc),
                ('opb1', cvb_in[c_bits*(i+1):c_bits*(i+2)]),
                ('opbv', cvb_v_in[i+1]),
                ('da', dvbc_t[i*dist_bits:dist_bits*(i+1)]),
                ('db', dvbc_t[dist_bits*(i+1):dist_bits*(i+2)]),
            ]
            aux = self.create_distance_rom()
            m.Instance(aux, '%s_dbc_%d' % (aux.name, (i // 2)), par, con)

        # -----

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st5_d2_s1(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "st5_d2_s1_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        ca_in = m.Input('ca_in', c_bits)
        cb_in = m.Input('cb_in', c_bits)
        cva_in = m.Input('cva_in', c_bits*n_neighbors)
        cva_v_in = m.Input('cva_v_in', n_neighbors)
        cvb_in = m.Input('cvb_in', c_bits*n_neighbors)
        cvb_v_in = m.Input('cvb_v_in', n_neighbors)
        dvac_in = m.Input('dvac_in', n_neighbors*dist_bits)
        dvbc_in = m.Input('dvbc_in', n_neighbors*dist_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        dvac_out = m.OutputReg('dvac_out', n_neighbors//2*dist_bits)
        dvbc_out = m.OutputReg('dvbc_out', n_neighbors//2*dist_bits)
        dvas_out = m.OutputReg('dvas_out', n_neighbors*dist_bits)
        dvbs_out = m.OutputReg('dvbs_out', n_neighbors*dist_bits)
        # -----

        cas = m.Wire('cas', c_bits)
        cbs = m.Wire('cbs', c_bits)
        opva = m.Input('opva', c_bits*n_neighbors)
        opvb = m.Input('opvb', c_bits*n_neighbors)
        dvac_t = m.Wire('dvac_t', dvac_out.width)
        dvbc_t = m.Wire('dvbc_t', dvbc_out.width)
        dvas_t = m.Wire('dvas_t', n_neighbors*dist_bits)
        dvbs_t = m.Wire('dvbs_t', n_neighbors*dist_bits)
        cas.assign(cb_in)
        cbs.assign(ca_in)

        for i in range(0, (n_neighbors//2)+1, 2):
            n = i // 2
            dvac_t[n*dist_bits:dist_bits*(n+1)].assign(
                dvac_in[i*dist_bits:dist_bits*(i+1)] + dvac_in[dist_bits*(i+1):dist_bits*(i+2)])

        for i in range(0, (n_neighbors//2)+1, 2):
            n = i // 2
            dvbc_t[n*dist_bits:dist_bits*(n+1)].assign(
                dvbc_in[i*dist_bits:dist_bits*(i+1)] + dvbc_in[dist_bits*(i+1):dist_bits*(i+2)])

        for i in range(n_neighbors):
            opva[i*c_bits:c_bits*(i+1)].assign(Mux(cva_in[i*c_bits:c_bits*(i+1)]
                                                   == cas, cbs, cva_in[i*c_bits:c_bits*(i+1)]))

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            dvac_out(dvac_t),
            dvbc_out(dvbc_t),
            dvas_out(dvas_t),
            dvbs_out(dvbs_t),
        )

        for i in range(0, (n_neighbors//2)+1, 2):
            par = []
            con = [
                ('opa0', cas),
                ('opa1', opva[i*c_bits:c_bits*(i+1)]),
                ('opav', cva_v_in[i]),
                ('opb0', cas),
                ('opb1', opva[c_bits*(i+1):c_bits*(i+2)]),
                ('opbv', cva_v_in[i+1]),
                ('da', dvas_t[i*dist_bits:dist_bits*(i+1)]),
                ('db', dvas_t[dist_bits*(i+1):dist_bits*(i+2)]),
            ]
            aux = self.create_distance_rom()
            m.Instance(aux, '%s_das_%d' % (aux.name, (i // 2)), par, con)

        for i in range(0, (n_neighbors//2)+1, 2):
            par = []
            con = [
                ('opa0', cbs),
                ('opa1', opvb[i*c_bits:c_bits*(i+1)]),
                ('opav', cvb_v_in[i]),
                ('opb0', cbs),
                ('opb1', opvb[c_bits*(i+1):c_bits*(i+2)]),
                ('opbv', cvb_v_in[i+1]),
                ('da', dvbs_t[i*dist_bits:dist_bits*(i+1)]),
                ('db', dvbs_t[dist_bits*(i+1):dist_bits*(i+2)]),
            ]
            aux = self.create_distance_rom()
            m.Instance(aux, '%s_dbs_%d' % (aux.name, (i // 2)), par, con)

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st6_s2(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "st6_s2_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        dvac_in = m.Input('dvac_in', n_neighbors//2*dist_bits)
        dvbc_in = m.Input('dvbc_in', n_neighbors//2*dist_bits)
        dvas_in = m.Input('dvas_in', n_neighbors*dist_bits)
        dvbs_in = m.Input('dvbs_in', n_neighbors*dist_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        dvac_out = m.OutputReg('dvac_out', dist_bits)
        dvbc_out = m.OutputReg('dvbc_out', dist_bits)
        dvas_out = m.OutputReg('dvas_out', n_neighbors//2*dist_bits)
        dvbs_out = m.OutputReg('dvbs_out', n_neighbors//2*dist_bits)
        # -----

        dvac_t = m.Wire('dvac_t', dvac_out.width)
        dvbc_t = m.Wire('dvbc_t', dvbc_out.width)
        dvas_t = m.Wire('dvas_t', dvas_out.width)
        dvbs_t = m.Wire('dvbs_t', dvbs_out.width)

        dvac_t.assign(dvac_in[0:dist_bits] + dvac_in[dist_bits:dist_bits*2])
        dvbc_t.assign(dvbc_in[0:dist_bits] + dvbc_in[dist_bits:dist_bits*2])

        for i in range(0, (n_neighbors//2)+1, 2):
            n = i // 2
            dvas_t[n*dist_bits:dist_bits*(n+1)].assign(
                dvas_in[i*dist_bits:dist_bits*(i+1)] + dvas_in[dist_bits*(i+1):dist_bits*(i+2)])

        for i in range(0, (n_neighbors//2)+1, 2):
            n = i // 2
            dvbs_t[n*dist_bits:dist_bits*(n+1)].assign(
                dvbs_in[i*dist_bits:dist_bits*(i+1)] + dvbs_in[dist_bits*(i+1):dist_bits*(i+2)])

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            dvac_out(dvac_t),
            dvbc_out(dvbc_t),
            dvas_out(dvas_t),
            dvbs_out(dvbs_t),
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st7_s3(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "st7_s3_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        dvac_in = m.Input('dvac_in', dist_bits)
        dvbc_in = m.Input('dvbc_in', dist_bits)
        dvas_in = m.Input('dvas_in', n_neighbors//2*dist_bits)
        dvbs_in = m.Input('dvbs_in', n_neighbors//2*dist_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        dc_out = m.OutputReg('dc_out', dist_bits)
        dvas_out = m.OutputReg('dvas_out', dist_bits)
        dvbs_out = m.OutputReg('dvbs_out', dist_bits)
        # -----

        dc_t = m.Wire('dc_t', dc_out.width)
        dvas_t = m.Wire('dvas_t', dvas_out.width)
        dvbs_t = m.Wire('dvbs_t', dvbs_out.width)

        dc_t.assign(dvac_in + dvbc_in)
        dvas_t.assign(dvas_in[0:dist_bits] + dvas_in[dist_bits:dist_bits*2])
        dvbs_t.assign(dvbs_in[0:dist_bits] + dvbs_in[dist_bits:dist_bits*2])

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            dc_out(dc_t),
            dvas_out(dvas_t),
            dvbs_out(dvbs_t),
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st8_s4(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "st8_s4_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        dc_in = m.Input('dc_in', dist_bits)
        dvas_in = m.Input('dvas_in', dist_bits)
        dvbs_in = m.Input('dvbs_in', dist_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        dc_out = m.OutputReg('dc_out', dist_bits)
        ds_out = m.OutputReg('ds_out', dist_bits)
        # -----

        ds_t = m.Wire('ds_t', ds_out.width)

        ds_t.assign(dvas_in + dvbs_in)

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            dc_out(dc_in),
            ds_out(ds_t),
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st9_cmp(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "st9_cmp_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        dc_in = m.Input('dc_in', dist_bits)
        ds_in = m.Input('ds_in', dist_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        sw_out = m.OutputReg('sw_out')
        # -----

        sw_t = m.Wire('sw_t')
        sw_t.assign(ds_in < dc_in)

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            sw_out(sw_t)
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st10_reg(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "st10_reg_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        sw_in = m.Input('sw_in')

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        sw_out = m.OutputReg('sw_out')

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            sw_out(sw_in)
        )

        # -----

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_sa_pipeline(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = "sa_pipeline_%dth_%dcells" % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits+c_bits+node_bits+1
        dist_bits = c_bits + ceil(log2(n_neighbors*2))

        m = Module(name)

        m.EmbeddedCode('// basic control inputs')
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        m.EmbeddedCode('// -----')

        # Threads controller output wires
        m.EmbeddedCode('// Threads controller output wires')
        th_idx = m.Wire('th_idx', t_bits)
        th_v = m.Wire('th_v')
        th_ca = m.Wire('th_ca', c_bits)
        th_cb = m.Wire('th_cb', c_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st1 output wires
        m.EmbeddedCode('// st1 output wires')
        st1_idx = m.Wire('st1_idx', t_bits)
        st1_v = m.Wire('st1_v')
        st1_ca = m.Wire('st1_ca', c_bits)
        st1_cb = m.Wire('st1_cb', c_bits)
        st1_na = m.Wire('st1_na', node_bits)
        st1_na_v = m.Wire('st1_na_v')
        st1_nb = m.Wire('st1_nb', node_bits)
        st1_nb_v = m.Wire('st1_nb_v')
        st1_sw = m.Wire('st1_sw')
        st1_wa = m.Wire('st1_wa', w_bits)
        st1_wb = m.Wire('st1_wb', w_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st2 output wires
        m.EmbeddedCode('// st2 output wires')
        st2_idx = m.Wire('st2_idx', t_bits)
        st2_v = m.Wire('st2_v')
        st2_ca = m.Wire('st2_ca', c_bits)
        st2_cb = m.Wire('st2_cb', c_bits)
        st2_na = m.Wire('st2_na', node_bits)
        st2_na_v = m.Wire('st2_na_v')
        st2_nb = m.Wire('st2_nb', node_bits)
        st2_nb_v = m.Wire('st2_nb_v')
        st2_va = m.Wire('st2_va', node_bits*n_neighbors)
        st2_va_v = m.Wire('st2_va_v', n_neighbors)
        st2_vb = m.Wire('st2_vb', node_bits*n_neighbors)
        st2_vb_v = m.Wire('st2_vb_v', n_neighbors)
        st2_sw = m.Wire('st2_sw')
        st2_wa = m.Wire('st2_wa', w_bits)
        st2_wb = m.Wire('st2_wb', w_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st3 output wires
        m.EmbeddedCode('// st3 output wires')
        st3_idx = m.Wire('st3_idx', t_bits)
        st3_v = m.Wire('st3_v')
        st3_ca = m.Wire('st3_ca', c_bits)
        st3_cb = m.Wire('st3_cb', c_bits)
        st3_cva = m.Wire('st3_cva', c_bits*n_neighbors)
        st3_cva_v = m.Wire('st3_cva_v', n_neighbors)
        st3_cvb = m.Wire('st3_cvb', c_bits*n_neighbors)
        st3_cvb_v = m.Wire('st3_cvb_v', n_neighbors)
        st3_wb = m.Wire('st3_wb', w_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st4 output wires
        m.EmbeddedCode('// st4 output wires')
        st4_idx = m.Wire('st4_idx', t_bits)
        st4_v = m.Wire('st4_v')
        st4_ca = m.Wire('st4_ca', c_bits)
        st4_cb = m.Wire('st4_cb', c_bits)
        st4_cva = m.Wire('st4_cva', c_bits*n_neighbors)
        st4_cva_v = m.Wire('st4_cva_v', n_neighbors)
        st4_cvb = m.Wire('st4_cvb', c_bits*n_neighbors)
        st4_cvb_v = m.Wire('st4_cvb_v', n_neighbors)
        st4_dvac = m.Wire('st4_dvac', n_neighbors*dist_bits)
        st4_dvbc = m.Wire('st4_dvbc', n_neighbors*dist_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st5 output wires
        m.EmbeddedCode('// st5 output wires')
        st5_idx = m.Wire('st5_idx', t_bits)
        st5_v = m.Wire('st5_v')
        st5_dvac = m.Wire('st5_dvac', n_neighbors//2*dist_bits)
        st5_dvbc = m.Wire('st5_dvbc', n_neighbors//2*dist_bits)
        st5_dvas = m.Wire('st5_dvas', n_neighbors*dist_bits)
        st5_dvbs = m.Wire('st5_dvbs', n_neighbors*dist_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st6 output wires
        m.EmbeddedCode('// st6 output wires')
        st6_idx = m.Wire('st6_idx', t_bits)
        st6_v = m.Wire('st6_v')
        st6_dvac = m.Wire('st6_dvac', dist_bits)
        st6_dvbc = m.Wire('st6_dvbc', dist_bits)
        st6_dvas = m.Wire('st6_dvas', n_neighbors//2*dist_bits)
        st6_dvbs = m.Wire('st6_dvbs', n_neighbors//2*dist_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st7 output wires
        m.EmbeddedCode('// st7 output wires')
        st7_idx = m.Wire('st7_idx', t_bits)
        st7_v = m.Wire('st7_v')
        st7_dc = m.Wire('st7_dc', dist_bits)
        st7_dvas = m.Wire('st7_dvas', dist_bits)
        st7_dvbs = m.Wire('st7_dvbs', dist_bits)

        # st8 output wires
        m.EmbeddedCode('// st8 output wires')
        st8_idx = m.Wire('st8_idx', t_bits)
        st8_v = m.Wire('st8_v')
        st8_dc = m.Wire('st8_dc', dist_bits)
        st8_ds = m.Wire('st8_ds', dist_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st9 output wires
        m.EmbeddedCode('// st10 output wires')
        st9_idx = m.OutputReg('st9_idx', t_bits)
        st9_v = m.OutputReg('st9_v')
        st9_sw = m.OutputReg('st9_sw')
        m.EmbeddedCode('// -----')
        # -----

        # st10 output wires
        m.EmbeddedCode('// st10 output wires')
        st10_idx = m.OutputReg('st10_idx', t_bits)
        st10_v = m.OutputReg('st10_v')
        st10_sw = m.Wire('st10_sw')
        m.EmbeddedCode('// -----')
        # -----

        # modules instantiations
        par = []
        con = [
            ('clk', clk),
            ('idx_in', th_idx),
            ('v_in', th_v),
            ('ca_in', th_ca),
            ('cb_in', th_cb),
            ('sw_in', st10_sw),
            ('st1_wb_in', st1_wb),
            ('idx_out', st1_idx),
            ('v_out', st1_v),
            ('ca_out', st1_ca),
            ('cb_out', st1_cb),
            ('na_out', st1_na),
            ('na_v_out', st1_na_v),
            ('nb_out', st1_nb),
            ('nb_v_out', st1_nb_v),
            ('sw_out', st1_sw),
            ('wa_out', st1_wa),
            ('wb_out', st1_wb)
        ]
        aux = self.create_st1_c2n()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st1_idx),
            ('v_in', st1_v),
            ('ca_in', st1_ca),
            ('cb_in', st1_cb),
            ('na_in', st1_na),
            ('na_v_in', st1_na_v),
            ('nb_in', st1_nb),
            ('nb_v_in', st1_nb_v),
            ('sw_in', st1_sw),
            ('wa_in', st1_wa),
            ('wb_in', st1_wb),
            ('idx_out', st2_idx),
            ('v_out', st2_v),
            ('ca_out', st2_ca),
            ('cb_out', st2_cb),
            ('na_out', st2_na),
            ('na_v_out', st2_na_v),
            ('nb_out', st2_nb),
            ('nb_v_out', st2_nb_v),
            ('va_out', st2_va),
            ('va_v_out', st2_va_v),
            ('vb_out', st2_vb),
            ('vb_v_out', st2_vb_v),
            ('sw_out', st2_sw),
            ('wa_out', st2_wa),
            ('wb_out', st2_wb),
        ]
        aux = self.create_st2_n()
        m.Instance(aux, aux.name, par, con)

        pa = []
        con = [
            ('clk', clk),
            ('idx_in', st2_idx),
            ('v_in', st2_v),
            ('ca_in', st2_ca),
            ('cb_in', st2_cb),
            ('na_in', st2_na),
            ('na_v_in', st2_na_v),
            ('nb_in', st2_nb),
            ('nb_v_in', st2_nb_v),
            ('va_in', st2_va),
            ('va_v_in', st2_va_v),
            ('vb_in', st2_vb),
            ('vb_v_in', st2_vb_v),
            ('st3_wb_in', st3_wb),
            ('sw_in', st2_sw),
            ('wa_in', st2_wa),
            ('wb_in', st2_wb),
            ('idx_out', st3_idx),
            ('v_out', st3_v),
            ('ca_out', st3_ca),
            ('cb_out', st3_cb),
            ('cva_out', st3_cva),
            ('cva_v_out', st3_cva_v),
            ('cvb_out', st3_cvb),
            ('cvb_v_out', st3_cvb_v),
            ('wb_out', st3_wb)
        ]
        aux = self.create_st3_n2c()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st3_idx),
            ('v_in', st3_v),
            ('ca_in', st3_ca),
            ('cb_in', st3_cb),
            ('cva_in', st3_cva),
            ('cva_v_in', st3_cva_v),
            ('cvb_in', st3_cvb),
            ('cvb_v_in', st3_cvb_v),
            ('idx_out', st4_idx),
            ('v_out', st4_v),
            ('ca_out', st4_ca),
            ('cb_out', st4_cb),
            ('cva_out', st4_cva),
            ('cva_v_out', st4_cva_v),
            ('cvb_out', st4_cvb),
            ('cvb_v_out', st4_cvb_v),
            ('dvac_out', st4_dvac),
            ('dvbc_out', st4_dvbc)
        ]
        aux = self.create_st4_d1()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st4_idx),
            ('v_in', st4_v),
            ('ca_in', st4_ca),
            ('cb_in', st4_cb),
            ('cva_in', st4_cva),
            ('cva_v_in', st4_cva_v),
            ('cvb_in', st4_cvb),
            ('cvb_v_in', st4_cvb_v),
            ('dvac_in', st4_dvac),
            ('dvbc_in', st4_dvbc),
            ('idx_out', st4_idx),
            ('v_out', st5_v),
            ('dvac_out', st5_dvac),
            ('dvbc_out', st5_dvbc),
            ('dvas_out', st5_dvas),
            ('dvbs_out', st5_dvbs)
        ]
        aux = self.create_st5_d2_s1()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st5_idx),
            ('v_in', st5_v),
            ('dvac_in', st5_dvac),
            ('dvbc_in', st5_dvbc),
            ('dvas_in', st5_dvas),
            ('dvbs_in', st5_dvbs),
            ('idx_out', st6_idx),
            ('v_out', st6_v),
            ('dvac_out', st6_dvac),
            ('dvbc_out', st6_dvbc),
            ('dvas_out', st6_dvas),
            ('dvbs_out', st6_dvbs)

        ]
        aux = self.create_st6_s2()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st6_idx),
            ('v_in', st6_v),
            ('dvac_in', st6_dvac),
            ('dvbc_in', st6_dvbc),
            ('dvas_in', st6_dvas),
            ('dvbs_in', st6_dvbs),
            ('idx_out', st7_idx),
            ('v_out', st7_v),
            ('dc_out', st7_dc),
            ('dvas_out', st7_dvas),
            ('dvbs_out', st7_dvbs)
        ]
        aux = self.create_st7_s3()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st7_idx),
            ('v_in', st7_v),
            ('dc_in', st7_dc),
            ('dvas_in', st7_dvas),
            ('dvbs_in', st7_dvbs),
            ('idx_out', st8_idx),
            ('v_out', st8_v),
            ('dc_out', st8_dc),
            ('ds_out', st8_ds)
        ]
        aux = self.create_st8_s4()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st8_idx),
            ('v_in', st8_v),
            ('dc_in', st8_dc),
            ('ds_in', st8_ds),
            ('idx_out', st9_idx),
            ('v_out', st9_v),
            ('sw_out', st9_sw)
        ]
        aux = self.create_st9_cmp()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st9_idx),
            ('v_in', st9_v),
            ('sw_in', st9_sw),
            ('idx_out', st10_idx),
            ('v_out', st10_v),
            ('sw_out', st10_sw)
        ]
        aux = self.create_st10_reg()
        m.Instance(aux, aux.name, par, con)
        # -----

        initialize_regs(m)
        self.cache[name] = m
        return m
