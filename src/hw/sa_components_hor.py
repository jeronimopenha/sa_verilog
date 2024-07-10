from math import ceil, log2, sqrt
from veriloggen import *
from src.utils.sa_graph import SaGraph
from src.hw.sa_components import SaComponents
from src.utils.util import Util


class SASaComponentsHor(SaComponents):
    def __init__(self, sa_graph: SaGraph, n_threads: int = 6, n_neighbors: int = 4, align_bits: int = 8):
        super().__init__(sa_graph, n_threads, n_neighbors, align_bits)

    def create_st1_c2n(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'st1_c2n_%dth_%dcells' % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))

        m = Module(name)
        clk = m.Input('clk')
        rst = m.Input('rst')

        # input config interfaces
        st1_wr = m.Input('st1_wr')
        st1_wr_addr = m.Input('st1_wr_addr', t_bits + c_bits)
        st1_wr_data = m.Input('st1_wr_data', node_bits + 1)

        # output_data_interface
        rd = m.Input('rd')
        rd_addr = m.Input('rd_addr', t_bits + c_bits)
        out_v = m.OutputReg('out_v')
        out_data = m.OutputReg('out_data', node_bits + 1)

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        ca_in = m.Input('ca_in', c_bits)
        cb_in = m.Input('cb_in', c_bits)
        sw_in = m.Input('sw_in')
        st1_wb_in = m.Input('st1_wb_in', w_bits)
        st10_wa_in = m.Input('st10_wa_in', w_bits)
        st10_wb_in = m.Input('st10_wb_in', w_bits)

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
        pwa_out = m.OutputReg('pwa_out', w_bits)
        pwb_out = m.OutputReg('pwb_out', w_bits)
        # -----

        flag = m.Reg('flag')

        na_t = m.Wire('na_t', node_bits)
        na_v_t = m.Wire('na_v_t')
        nb_t = m.Wire('nb_t', node_bits)
        nb_v_t = m.Wire('nb_v_t')

        pwa_t = m.Wire('pwa_t', w_bits)
        pwb_t = m.Wire('pwb_t', w_bits)

        wa_idx = m.Wire('wa_idx', t_bits)
        wa_c = m.Wire('wa_c', c_bits)
        wa_n = m.Wire('wa_n', node_bits)
        wa_n_v = m.Wire('wa_n_v')

        wb_idx = m.Wire('wb_idx', t_bits)
        wb_c = m.Wire('wb_c', c_bits)
        wb_n = m.Wire('wb_n', node_bits)
        wb_n_v = m.Wire('wb_n_v')

        m_wr = m.Wire('m_wr')
        m_wr_addr = m.Wire('m_wr_addr', c_bits + t_bits)
        m_wr_data = m.Wire('m_wr_data', node_bits + 1)

        m.EmbeddedCode('')

        pwa_t.assign(Cat(idx_in, ca_in, nb_v_t, nb_t))
        pwb_t.assign(Cat(idx_in, cb_in, na_v_t, na_t))

        m.EmbeddedCode('')

        i = 0
        wa_n.assign(st10_wa_in[i: node_bits])
        i += node_bits
        wa_n_v.assign(st10_wa_in[i])
        i += 1
        wa_c.assign(st10_wa_in[i: c_bits + i])
        i += c_bits
        wa_idx.assign(st10_wa_in[i: t_bits + i])

        m.EmbeddedCode('')

        i = 0
        wb_n.assign(st1_wb_in[i: node_bits])
        i += node_bits
        wb_n_v.assign(st1_wb_in[i])
        i += 1
        wb_c.assign(st1_wb_in[i: c_bits + i])
        i += c_bits
        wb_idx.assign(st1_wb_in[i: t_bits + i])

        m.EmbeddedCode('')

        m_wr.assign(sw_in)
        m_wr_addr.assign(Mux(flag, Cat(wa_idx, wa_c), Cat(wb_idx, wb_c)))
        m_wr_data.assign(Mux(flag, Cat(wa_n_v, wa_n), Cat(wb_n_v, wb_n)))

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            ca_out(ca_in),
            cb_out(cb_in),
            na_out(na_t),
            na_v_out(na_v_t),
            nb_out(nb_t),
            nb_v_out(nb_v_t),
            sw_out(sw_in),
            wa_out(st10_wa_in),
            wb_out(st10_wb_in),
            pwa_out(pwa_t),
            pwb_out(pwb_t),
            out_v(rd),
            out_data(Cat(na_v_t, na_t))
        )

        m.Always(Posedge(clk))(
            If(rst)(
                flag(1)
            ).Else(
                If(sw_in)(
                    flag(~flag)
                )
            )
        )

        par = [
            ('init_file', './c_n.rom'),
            ('read_f', 1),
            ('write_f', 1),
            ('output_file', './c_n_out.rom')
        ]
        con = [
            ('clk', clk),
            ('rd_addr0', Mux(rd, rd_addr, Cat(idx_in, ca_in))),
            ('rd_addr1', Cat(idx_in, cb_in)),
            ('out0', Cat(na_v_t, na_t)),
            ('out1', Cat(nb_v_t, nb_t)),
            ('wr', Uor(Cat(m_wr, st1_wr))),
            ('wr_addr', Mux(st1_wr, st1_wr_addr, m_wr_addr)),
            ('wr_data', Mux(st1_wr, st1_wr_data, m_wr_data)),
        ]
        aux = self.create_memory_2r_1w(node_bits + 1, t_bits + c_bits)
        m.Instance(aux, aux.name, par, con)

        Util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st2_n(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'st2_n_%dth_%dcells' % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))
        m_n_bits = (node_bits * n_neighbors) + n_neighbors

        m = Module(name)
        clk = m.Input('clk')

        # config_interface
        st2_wr = m.Input('st2_wr', n_neighbors)
        st2_wr_addr = m.Input('st2_wr_addr', node_bits)
        st2_wr_data = m.Input('st2_wr_data', node_bits + 1)

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
        pwa_in = m.Input('pwa_in', w_bits)
        pwb_in = m.Input('pwb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        ca_out = m.OutputReg('ca_out', c_bits)
        cb_out = m.OutputReg('cb_out', c_bits)
        na_out = m.OutputReg('na_out', node_bits)
        na_v_out = m.OutputReg('na_v_out')
        nb_out = m.OutputReg('nb_out', node_bits)
        nb_v_out = m.OutputReg('nb_v_out')
        va_out = m.OutputReg('va_out', node_bits * n_neighbors)
        va_v_out = m.OutputReg('va_v_out', n_neighbors)
        vb_out = m.OutputReg('vb_out', node_bits * n_neighbors)
        vb_v_out = m.OutputReg('vb_v_out', n_neighbors)
        sw_out = m.OutputReg('sw_out')
        wa_out = m.OutputReg('wa_out', w_bits)
        wb_out = m.OutputReg('wb_out', w_bits)
        pwa_out = m.OutputReg('pwa_out', w_bits)
        pwb_out = m.OutputReg('pwb_out', w_bits)

        m.EmbeddedCode('')

        va_t = m.Wire('va_t', node_bits * n_neighbors)
        va_v_t = m.Wire('va_v_t', n_neighbors)
        va_v_m = m.Wire('va_v_m', n_neighbors)
        vb_t = m.Wire('vb_t', node_bits * n_neighbors)
        vb_v_t = m.Wire('vb_v_t', n_neighbors)
        vb_v_m = m.Wire('vb_v_m', n_neighbors)

        va_v_t.assign(Mux(na_v_in, va_v_m, Int(0, n_neighbors, 2)))
        vb_v_t.assign(Mux(nb_v_in, vb_v_m, Int(0, n_neighbors, 2)))

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            ca_out(ca_in),
            cb_out(cb_in),
            na_out(na_in),
            na_v_out(na_v_in),
            nb_out(nb_in),
            nb_v_out(nb_v_in),
            sw_out(sw_in),
            wa_out(wa_in),
            wb_out(wb_in),
            va_out(va_t),
            va_v_out(va_v_t),
            vb_out(vb_t),
            vb_v_out(vb_v_t),
            pwa_out(pwa_in),
            pwb_out(pwb_out)
        )

        for i in range(n_neighbors):
            par = [
                ('init_file', './n%d.rom' % i),
                ('read_f', 1),
                ('write_f', 0)
            ]
            con = [
                ('clk', clk),
                ('rd_addr0', na_in),
                ('rd_addr1', nb_in),
                ('out0', Cat(va_v_m[i],
                             va_t[node_bits * i:node_bits * (i + 1)])),
                ('out1', Cat(vb_v_m[i],
                             vb_t[node_bits * i:node_bits * (i + 1)])),
                ('wr', st2_wr[i]),
                ('wr_addr', st2_wr_addr),
                ('wr_data', st2_wr_data),
            ]
            aux = self.create_memory_2r_1w(node_bits + 1, node_bits)
            m.Instance(aux, '%s_%i' % (aux.name, i), par, con)

        Util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st3_n2c(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'st3_n2c_%dth_%dcells' % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))

        m = Module(name)
        clk = m.Input('clk')
        rst = m.Input('rst')

        # config interface
        st3_wr = m.Input('st3_wr')
        st3_wr_addr = m.Input('st3_wr_addr', t_bits + node_bits)
        st3_wr_data = m.Input('st3_wr_data', c_bits)

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        ca_in = m.Input('ca_in', c_bits)
        cb_in = m.Input('cb_in', c_bits)
        na_in = m.Input('na_in', node_bits)
        na_v_in = m.Input('na_v_in')
        nb_in = m.Input('nb_in', node_bits)
        nb_v_in = m.Input('nb_v_in')
        va_in = m.Input('va_in', node_bits * n_neighbors)
        va_v_in = m.Input('va_v_in', n_neighbors)
        vb_in = m.Input('vb_in', node_bits * n_neighbors)
        vb_v_in = m.Input('vb_v_in', n_neighbors)
        st3_wb_in = m.Input('st3_wb_in', w_bits)
        sw_in = m.Input('sw_in')
        wa_in = m.Input('wa_in', w_bits)
        wb_in = m.Input('wb_in', w_bits)
        pwa_in = m.Input('pwa_in', w_bits)
        pwb_in = m.Input('pwb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        ca_out = m.OutputReg('ca_out', c_bits)
        cb_out = m.OutputReg('cb_out', c_bits)
        cva_out = m.OutputReg('cva_out', c_bits * n_neighbors)
        cva_v_out = m.OutputReg('cva_v_out', n_neighbors)
        cvb_out = m.OutputReg('cvb_out', c_bits * n_neighbors)
        cvb_v_out = m.OutputReg('cvb_v_out', n_neighbors)
        wa_out = m.OutputReg('wa_out', w_bits)
        wb_out = m.OutputReg('wb_out', w_bits)
        pwa_out = m.OutputReg('pwa_out', w_bits)
        pwb_out = m.OutputReg('pwb_out', w_bits)
        # -----

        flag = m.Reg('flag')
        cva_t = m.Wire('cva_t', c_bits * n_neighbors)
        cvb_t = m.Wire('cvb_t', c_bits * n_neighbors)

        wa_idx = m.Wire('wa_idx', t_bits)
        wa_c = m.Wire('wa_c', c_bits)
        wa_n = m.Wire('wa_n', node_bits)
        wa_n_v = m.Wire('wa_n_v')
        wb_idx = m.Wire('wb_idx', t_bits)
        wb_c = m.Wire('wb_c', c_bits)
        wb_n = m.Wire('wb_n', node_bits)
        wb_n_v = m.Wire('wb_n_v')

        m_wr = m.Wire('m_wr')
        m_wr_addr = m.Wire('m_wr_addr', c_bits + t_bits)
        m_wr_data = m.Wire('m_wr_data', c_bits)

        i = 0
        wa_n.assign(wa_in[i:node_bits])
        i += node_bits
        wa_n_v.assign(wa_in[i])
        i += 1
        wa_c.assign(wa_in[i:c_bits + i])
        i += c_bits
        wa_idx.assign(wa_in[i:t_bits + i])

        i = 0
        wb_n.assign(st3_wb_in[i:node_bits])
        i += node_bits
        wb_n_v.assign(st3_wb_in[i])
        i += 1
        wb_c.assign(st3_wb_in[i:c_bits + i])
        i += c_bits
        wb_idx.assign(st3_wb_in[i:t_bits + i])

        m_wr.assign(Mux(flag, Uand(Cat(sw_in, wa_n_v)),
                        Uand(Cat(sw_in, wb_n_v))))
        m_wr_addr.assign(Mux(flag, Cat(wa_idx, wa_n), Cat(wb_idx, wb_n)))
        m_wr_data.assign(Mux(flag, wa_c, wb_c))

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            ca_out(ca_in),
            cb_out(cb_in),
            cva_out(cva_t),
            cva_v_out(va_v_in),
            cvb_out(cvb_t),
            cvb_v_out(vb_v_in),
            wa_out(wa_in),
            wb_out(wb_in),
            pwa_out(pwa_in),
            pwb_out(pwb_in)
        )

        m.Always(Posedge(clk))(
            If(rst)(
                flag(1)
            ).Else(
                If(sw_in)(
                    flag(~flag)
                )
            )
        )

        for i in range(n_neighbors):
            par = [
                ('init_file', './n_c.rom'),
                ('read_f', 1),
                ('write_f', 1 if i == 0 else 0),
                ('output_file', './n_c_out.rom')
            ]
            con = [
                ('clk', clk),
                ('rd_addr0', Cat(idx_in, va_in[i * c_bits:c_bits * (i + 1)])),
                ('rd_addr1', Cat(idx_in, vb_in[i * c_bits:c_bits * (i + 1)])),
                ('out0', cva_t[i * c_bits:c_bits * (i + 1)]),
                ('out1', cvb_t[i * c_bits:c_bits * (i + 1)]),
                ('wr', Uor(Cat(m_wr, st3_wr))),
                ('wr_addr', Mux(st3_wr, st3_wr_addr, m_wr_addr)),
                ('wr_data', Mux(st3_wr, st3_wr_data, m_wr_data)),
            ]
            aux = self.create_memory_2r_1w(c_bits, t_bits + c_bits)
            m.Instance(aux, '%s_%d' % (aux.name, i), par, con)

        Util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st4_lcf(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'st4_lcf_%dth_%dcells' % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))
        lc_bits = ceil(log2(lines)) * 2

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        ca_in = m.Input('ca_in', c_bits)
        cb_in = m.Input('cb_in', c_bits)
        cva_in = m.Input('cva_in', c_bits * n_neighbors)
        cva_v_in = m.Input('cva_v_in', n_neighbors)
        cvb_in = m.Input('cvb_in', c_bits * n_neighbors)
        cvb_v_in = m.Input('cvb_v_in', n_neighbors)
        pwa_in = m.Input('pwa_in', w_bits)
        pwb_in = m.Input('pwb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        lca_out = m.OutputReg('lca_out', lc_bits)
        lcb_out = m.OutputReg('lcb_out', lc_bits)
        lcva_out = m.OutputReg('lcva_out', lc_bits * n_neighbors)
        lcva_v_out = m.OutputReg('lcva_v_out', n_neighbors)
        lcvb_out = m.OutputReg('lcvb_out', lc_bits * n_neighbors)
        lcvb_v_out = m.OutputReg('lcvb_v_out', n_neighbors)
        pwa_out = m.OutputReg('pwa_out', w_bits)
        pwb_out = m.OutputReg('pwb_out', w_bits)
        # -----

        lca_t = m.Wire('lca_t', lc_bits)
        lcb_t = m.Wire('lcb_t', lc_bits)
        lcva_t = m.Wire('lcva_t', lc_bits * n_neighbors)
        lcvb_t = m.Wire('lcvb_t', lc_bits * n_neighbors)

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            lca_out(lca_t),
            lcb_out(lcb_t),
            lcva_out(lcva_t),
            lcva_v_out(cva_v_in),
            lcvb_out(lcvb_t),
            lcvb_v_out(cvb_v_in),
            pwa_out(pwa_in),
            pwb_out(pwb_in)
        )

        aux = self.create_lc_table()
        par = []
        con = [
            ('ca', ca_in),
            ('cb', cb_in),
            ('lca', lca_t),
            ('lcb', lcb_t),
        ]
        m.Instance(aux, "%s_c" % aux.name, par, con)

        for i in range(n_neighbors):
            par = []
            con = [
                ('ca', cva_in[i * c_bits:c_bits * (i + 1)]),
                ('cb', cvb_in[i * c_bits:c_bits * (i + 1)]),
                ('lca', lcva_t[i * lc_bits:lc_bits * (i + 1)]),
                ('lcb', lcvb_t[i * lc_bits:lc_bits * (i + 1)]),
            ]
            m.Instance(aux, '%s_v_%d' % (aux.name, (i)), par, con)

        Util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st5_d1(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'st5_d1_%dth_%dcells' % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))
        lc_bits = ceil(log2(lines)) * 2

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        lca_in = m.Input('lca_in', lc_bits)
        lcb_in = m.Input('lcb_in', lc_bits)
        lcva_in = m.Input('lcva_in', lc_bits * n_neighbors)
        lcva_v_in = m.Input('lcva_v_in', n_neighbors)
        lcvb_in = m.Input('lcvb_in', lc_bits * n_neighbors)
        lcvb_v_in = m.Input('lcvb_v_in', n_neighbors)
        pwa_in = m.Input('pwa_in', w_bits)
        pwb_in = m.Input('pwb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        lca_out = m.OutputReg('lca_out', lc_bits)
        lcb_out = m.OutputReg('lcb_out', lc_bits)
        lcva_out = m.OutputReg('lcva_out', lc_bits * n_neighbors)
        lcva_v_out = m.OutputReg('lcva_v_out', n_neighbors)
        lcvb_out = m.OutputReg('lcvb_out', lc_bits * n_neighbors)
        lcvb_v_out = m.OutputReg('lcvb_v_out', n_neighbors)
        dvac_out = m.OutputReg('dvac_out', n_neighbors * dist_bits)
        dvbc_out = m.OutputReg('dvbc_out', n_neighbors * dist_bits)
        pwa_out = m.OutputReg('pwa_out', w_bits)
        pwb_out = m.OutputReg('pwb_out', w_bits)
        # -----

        lcac = m.Wire('lcac', c_bits)
        lcbc = m.Wire('lcbc', c_bits)
        dvac_t = m.Wire('dvac_t', n_neighbors * dist_bits)
        dvbc_t = m.Wire('dvbc_t', n_neighbors * dist_bits)

        lcac.assign(lca_in)
        lcbc.assign(lcb_in)

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            lca_out(lca_in),
            lcb_out(lcb_in),
            lcva_out(lcva_in),
            lcva_v_out(lcva_v_in),
            lcvb_out(lcvb_in),
            lcvb_v_out(lcvb_v_in),
            dvac_out(dvac_t),
            dvbc_out(dvbc_t),
            pwa_out(pwa_in),
            pwb_out(pwb_in)
        )

        for i in range(0, (n_neighbors // 2) + 1, 2):
            par = []
            con = [
                ('opa0', lcac),
                ('opa1', lcva_in[i * lc_bits:lc_bits * (i + 1)]),
                ('opav', lcva_v_in[i]),
                ('opb0', lcac),
                ('opb1', lcva_in[lc_bits * (i + 1):lc_bits * (i + 2)]),
                ('opbv', lcva_v_in[i + 1]),
                ('da', dvac_t[i * dist_bits:dist_bits * (i + 1)]),
                ('db', dvac_t[dist_bits * (i + 1):dist_bits * (i + 2)]),
            ]
            aux = self.create_distance_table()
            m.Instance(aux, '%s_dac_%d' % (aux.name, (i // 2)), par, con)

        for i in range(0, (n_neighbors // 2) + 1, 2):
            par = []
            con = [
                ('opa0', lcbc),
                ('opa1', lcvb_in[i * lc_bits:lc_bits * (i + 1)]),
                ('opav', lcvb_v_in[i]),
                ('opb0', lcbc),
                ('opb1', lcvb_in[lc_bits * (i + 1):lc_bits * (i + 2)]),
                ('opbv', lcvb_v_in[i + 1]),
                ('da', dvbc_t[i * dist_bits:dist_bits * (i + 1)]),
                ('db', dvbc_t[dist_bits * (i + 1):dist_bits * (i + 2)]),
            ]
            aux = self.create_distance_table()
            m.Instance(aux, '%s_dbc_%d' % (aux.name, (i // 2)), par, con)

        # -----

        Util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st6_d2_s1(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'st6_d2_s1_%dth_%dcells' % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))
        lc_bits = ceil(log2(lines)) * 2

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        lca_in = m.Input('lca_in', lc_bits)
        lcb_in = m.Input('lcb_in', lc_bits)
        lcva_in = m.Input('lcva_in', lc_bits * n_neighbors)
        lcva_v_in = m.Input('lcva_v_in', n_neighbors)
        lcvb_in = m.Input('lcvb_in', lc_bits * n_neighbors)
        lcvb_v_in = m.Input('lcvb_v_in', n_neighbors)
        dvac_in = m.Input('dvac_in', n_neighbors * dist_bits)
        dvbc_in = m.Input('dvbc_in', n_neighbors * dist_bits)
        pwa_in = m.Input('pwa_in', w_bits)
        pwb_in = m.Input('pwb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        dvac_out = m.OutputReg('dvac_out', n_neighbors // 2 * dist_bits)
        dvbc_out = m.OutputReg('dvbc_out', n_neighbors // 2 * dist_bits)
        dvas_out = m.OutputReg('dvas_out', n_neighbors * dist_bits)
        dvbs_out = m.OutputReg('dvbs_out', n_neighbors * dist_bits)
        pwa_out = m.OutputReg('pwa_out', w_bits)
        pwb_out = m.OutputReg('pwb_out', w_bits)
        # -----

        lcas = m.Wire('lcas', lc_bits)
        lcbs = m.Wire('lcbs', lc_bits)
        opva = m.Wire('opva', lc_bits * n_neighbors)
        opvb = m.Wire('opvb', lc_bits * n_neighbors)
        dvac_t = m.Wire('dvac_t', dvac_out.width)
        dvbc_t = m.Wire('dvbc_t', dvbc_out.width)
        dvas_t = m.Wire('dvas_t', n_neighbors * dist_bits)
        dvbs_t = m.Wire('dvbs_t', n_neighbors * dist_bits)
        lcas.assign(lcb_in)
        lcbs.assign(lca_in)

        for i in range(0, (n_neighbors // 2) + 1, 2):
            n = i // 2
            dvac_t[n * dist_bits:dist_bits * (n + 1)].assign(
                dvac_in[i * dist_bits:dist_bits * (i + 1)] + dvac_in[dist_bits * (i + 1):dist_bits * (i + 2)])

        for i in range(0, (n_neighbors // 2) + 1, 2):
            n = i // 2
            dvbc_t[n * dist_bits:dist_bits * (n + 1)].assign(
                dvbc_in[i * dist_bits:dist_bits * (i + 1)] + dvbc_in[dist_bits * (i + 1):dist_bits * (i + 2)])

        for i in range(n_neighbors):
            opva[i * lc_bits:lc_bits * (i + 1)].assign(Mux(lcva_in[i * lc_bits:lc_bits * (i + 1)]
                                                           == lcas, lcbs, lcva_in[i * lc_bits:lc_bits * (i + 1)]))

        for i in range(n_neighbors):
            opvb[i * lc_bits:lc_bits * (i + 1)].assign(Mux(lcvb_in[i * lc_bits:lc_bits * (i + 1)]
                                                           == lcbs, lcas, lcvb_in[i * lc_bits:lc_bits * (i + 1)]))

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            dvac_out(dvac_t),
            dvbc_out(dvbc_t),
            dvas_out(dvas_t),
            dvbs_out(dvbs_t),
            pwa_out(pwa_in),
            pwb_out(pwb_in)
        )

        for i in range(0, (n_neighbors // 2) + 1, 2):
            par = []
            con = [
                ('opa0', lcas),
                ('opa1', opva[i * lc_bits:lc_bits * (i + 1)]),
                ('opav', lcva_v_in[i]),
                ('opb0', lcas),
                ('opb1', opva[lc_bits * (i + 1):lc_bits * (i + 2)]),
                ('opbv', lcva_v_in[i + 1]),
                ('da', dvas_t[i * dist_bits:dist_bits * (i + 1)]),
                ('db', dvas_t[dist_bits * (i + 1):dist_bits * (i + 2)]),
            ]
            aux = self.create_distance_table()
            m.Instance(aux, '%s_das_%d' % (aux.name, (i // 2)), par, con)

        for i in range(0, (n_neighbors // 2) + 1, 2):
            par = []
            con = [
                ('opa0', lcbs),
                ('opa1', opvb[i * lc_bits:lc_bits * (i + 1)]),
                ('opav', lcvb_v_in[i]),
                ('opb0', lcbs),
                ('opb1', opvb[lc_bits * (i + 1):lc_bits * (i + 2)]),
                ('opbv', lcvb_v_in[i + 1]),
                ('da', dvbs_t[i * dist_bits:dist_bits * (i + 1)]),
                ('db', dvbs_t[dist_bits * (i + 1):dist_bits * (i + 2)]),
            ]
            aux = self.create_distance_table()
            m.Instance(aux, '%s_dbs_%d' % (aux.name, (i // 2)), par, con)

        Util.initialize_regs(m)
        self.cache[name] = m
        return m
        lc_bits = ceil(log2(lines)) * 2

    def create_st7_s2(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'st7_s2_%dth_%dcells' % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        dvac_in = m.Input('dvac_in', n_neighbors // 2 * dist_bits)
        dvbc_in = m.Input('dvbc_in', n_neighbors // 2 * dist_bits)
        dvas_in = m.Input('dvas_in', n_neighbors * dist_bits)
        dvbs_in = m.Input('dvbs_in', n_neighbors * dist_bits)
        pwa_in = m.Input('pwa_in', w_bits)
        pwb_in = m.Input('pwb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        dvac_out = m.OutputReg('dvac_out', dist_bits)
        dvbc_out = m.OutputReg('dvbc_out', dist_bits)
        dvas_out = m.OutputReg('dvas_out', n_neighbors // 2 * dist_bits)
        dvbs_out = m.OutputReg('dvbs_out', n_neighbors // 2 * dist_bits)
        pwa_out = m.OutputReg('pwa_out', w_bits)
        pwb_out = m.OutputReg('pwb_out', w_bits)
        # -----

        dvac_t = m.Wire('dvac_t', dvac_out.width)
        dvbc_t = m.Wire('dvbc_t', dvbc_out.width)
        dvas_t = m.Wire('dvas_t', dvas_out.width)
        dvbs_t = m.Wire('dvbs_t', dvbs_out.width)

        dvac_t.assign(dvac_in[0:dist_bits] + dvac_in[dist_bits:dist_bits * 2])
        dvbc_t.assign(dvbc_in[0:dist_bits] + dvbc_in[dist_bits:dist_bits * 2])

        for i in range(0, (n_neighbors // 2) + 1, 2):
            n = i // 2
            dvas_t[n * dist_bits:dist_bits * (n + 1)].assign(
                dvas_in[i * dist_bits:dist_bits * (i + 1)] + dvas_in[dist_bits * (i + 1):dist_bits * (i + 2)])

        for i in range(0, (n_neighbors // 2) + 1, 2):
            n = i // 2
            dvbs_t[n * dist_bits:dist_bits * (n + 1)].assign(
                dvbs_in[i * dist_bits:dist_bits * (i + 1)] + dvbs_in[dist_bits * (i + 1):dist_bits * (i + 2)])

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            dvac_out(dvac_t),
            dvbc_out(dvbc_t),
            dvas_out(dvas_t),
            dvbs_out(dvbs_t),
            pwa_out(pwa_in),
            pwb_out(pwb_in)
        )

        Util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st8_s3(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'st8_s3_%dth_%dcells' % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        dvac_in = m.Input('dvac_in', dist_bits)
        dvbc_in = m.Input('dvbc_in', dist_bits)
        dvas_in = m.Input('dvas_in', n_neighbors // 2 * dist_bits)
        dvbs_in = m.Input('dvbs_in', n_neighbors // 2 * dist_bits)
        pwa_in = m.Input('pwa_in', w_bits)
        pwb_in = m.Input('pwb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        dc_out = m.OutputReg('dc_out', dist_bits)
        dvas_out = m.OutputReg('dvas_out', dist_bits)
        dvbs_out = m.OutputReg('dvbs_out', dist_bits)
        pwa_out = m.OutputReg('pwa_out', w_bits)
        pwb_out = m.OutputReg('pwb_out', w_bits)
        # -----

        dc_t = m.Wire('dc_t', dc_out.width)
        dvas_t = m.Wire('dvas_t', dvas_out.width)
        dvbs_t = m.Wire('dvbs_t', dvbs_out.width)

        dc_t.assign(dvac_in + dvbc_in)
        dvas_t.assign(dvas_in[0:dist_bits] + dvas_in[dist_bits:dist_bits * 2])
        dvbs_t.assign(dvbs_in[0:dist_bits] + dvbs_in[dist_bits:dist_bits * 2])

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            dc_out(dc_t),
            dvas_out(dvas_t),
            dvbs_out(dvbs_t),
            pwa_out(pwa_in),
            pwb_out(pwb_in)
        )

        Util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st9_s4(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'st9_s4_%dth_%dcells' % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        dc_in = m.Input('dc_in', dist_bits)
        dvas_in = m.Input('dvas_in', dist_bits)
        dvbs_in = m.Input('dvbs_in', dist_bits)
        pwa_in = m.Input('pwa_in', w_bits)
        pwb_in = m.Input('pwb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        dc_out = m.OutputReg('dc_out', dist_bits)
        ds_out = m.OutputReg('ds_out', dist_bits)
        pwa_out = m.OutputReg('pwa_out', w_bits)
        pwb_out = m.OutputReg('pwb_out', w_bits)
        # -----

        ds_t = m.Wire('ds_t', ds_out.width)

        ds_t.assign(dvas_in + dvbs_in)

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            dc_out(dc_in),
            ds_out(ds_t),
            pwa_out(pwa_in),
            pwb_out(pwb_in)
        )

        Util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_st10_cmp(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'st10_cmp_%dth_%dcells' % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        dc_in = m.Input('dc_in', dist_bits)
        ds_in = m.Input('ds_in', dist_bits)
        pwa_in = m.Input('pwa_in', w_bits)
        pwb_in = m.Input('pwb_in', w_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        sw_out = m.OutputReg('sw_out')
        wa_out = m.OutputReg('wa_out', w_bits)
        wb_out = m.OutputReg('wb_out', w_bits)
        # -----

        sw_t = m.Wire('sw_t')
        sw_t.assign(ds_in < dc_in)

        m.Always(Posedge(clk))(
            idx_out(idx_in),
            v_out(v_in),
            sw_out(sw_t),
            wa_out(pwa_in),
            wb_out(pwb_in)
        )

        Util.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_sa_pipeline(self) -> Module:
        sa_graph = self.sa_graph
        n_cells = self.sa_graph.n_cells
        n_neighbors = self.n_neighbors
        align_bits = self.align_bits
        n_threads = self.n_threads

        name = 'sa_pipeline_%dth_%dcells' % (n_threads, n_cells)
        if name in self.cache.keys():
            return self.cache[name]

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))
        lc_bits = ceil(log2(lines)) * 2

        m = Module(name)

        m.EmbeddedCode('// basic control inputs')
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        n_exec = m.Input('n_exec', 16)
        done = m.OutputReg('done')

        # input config interfaces
        st1_wr = m.Input('st1_wr')
        st1_wr_addr = m.Input('st1_wr_addr', t_bits + c_bits)
        st1_wr_data = m.Input('st1_wr_data', node_bits + 1)

        st2_wr = m.Input('st2_wr', n_neighbors)
        st2_wr_addr = m.Input('st2_wr_addr', node_bits)
        st2_wr_data = m.Input('st2_wr_data', node_bits + 1)

        st3_wr = m.Input('st3_wr')
        st3_wr_addr = m.Input('st3_wr_addr', t_bits + node_bits)
        st3_wr_data = m.Input('st3_wr_data', c_bits)

        # output_data_interface
        rd = m.Input('rd')
        rd_addr = m.Input('rd_addr', t_bits + c_bits)
        out_v = m.Output('out_v')
        out_data = m.Output('out_data', node_bits + 1)
        m.EmbeddedCode('// -----')

        pipe_start = m.Wire('pipe_start')
        counter_total = m.Reg('counter_total', n_exec.width + 1)

        # Threads controller output wires
        m.EmbeddedCode('// Threads controller output wires')
        th_idx = m.Wire('th_idx', t_bits)
        th_v = m.Wire('th_v')
        th_ca = m.Wire('th_ca', c_bits)
        th_cb = m.Wire('th_cb', c_bits)
        m.EmbeddedCode('// -----')
        # -----

        m.Always(Posedge(clk))(
            If(rst)(
                counter_total(0),
                done(0),
            ).Elif(pipe_start)(
                If(AndList(th_idx == n_threads - 1, ~th_v, Uand(Cat(th_ca, th_cb))))(
                    counter_total.inc(),
                ),
                If(counter_total == n_exec)(
                    done(1),
                )
            )
        )

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
        st1_pwa = m.Wire('st1_pwa', w_bits)
        st1_pwb = m.Wire('st1_pwb', w_bits)
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
        st2_va = m.Wire('st2_va', node_bits * n_neighbors)
        st2_va_v = m.Wire('st2_va_v', n_neighbors)
        st2_vb = m.Wire('st2_vb', node_bits * n_neighbors)
        st2_vb_v = m.Wire('st2_vb_v', n_neighbors)
        st2_sw = m.Wire('st2_sw')
        st2_wa = m.Wire('st2_wa', w_bits)
        st2_wb = m.Wire('st2_wb', w_bits)
        st2_pwa = m.Wire('st2_pwa', w_bits)
        st2_pwb = m.Wire('st2_pwb', w_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st3 output wires
        m.EmbeddedCode('// st3 output wires')
        st3_idx = m.Wire('st3_idx', t_bits)
        st3_v = m.Wire('st3_v')
        st3_ca = m.Wire('st3_ca', c_bits)
        st3_cb = m.Wire('st3_cb', c_bits)
        st3_cva = m.Wire('st3_cva', c_bits * n_neighbors)
        st3_cva_v = m.Wire('st3_cva_v', n_neighbors)
        st3_cvb = m.Wire('st3_cvb', c_bits * n_neighbors)
        st3_cvb_v = m.Wire('st3_cvb_v', n_neighbors)
        st3_wb = m.Wire('st3_wb', w_bits)
        st3_pwa = m.Wire('st3_pwa', w_bits)
        st3_pwb = m.Wire('st3_pwb', w_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st4 output wires
        m.EmbeddedCode('// st4 output wires')
        st4_idx = m.Wire('st4_idx', t_bits)
        st4_v = m.Wire('st4_v')
        st4_lca = m.Wire('st4_lca', lc_bits)
        st4_lcb = m.Wire('st4_lcb', lc_bits)
        st4_lcva = m.Wire('st4_lcva', lc_bits * n_neighbors)
        st4_lcva_v = m.Wire('st4_lcva_v', n_neighbors)
        st4_lcvb = m.Wire('st4_lcvb', lc_bits * n_neighbors)
        st4_lcvb_v = m.Wire('st4_lcvb_v', n_neighbors)
        st4_pwa = m.Wire('st4_pwa', w_bits)
        st4_pwb = m.Wire('st4_pwb', w_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st5 output wires
        m.EmbeddedCode('// st5 output wires')
        st5_idx = m.Wire('st5_idx', t_bits)
        st5_v = m.Wire('st5_v')
        st5_lca = m.Wire('st5_lca', lc_bits)
        st5_lcb = m.Wire('st5_lcb', lc_bits)
        st5_lcva = m.Wire('st5_lcva', lc_bits * n_neighbors)
        st5_lcva_v = m.Wire('st5_lcva_v', n_neighbors)
        st5_lcvb = m.Wire('st5_lcvb', lc_bits * n_neighbors)
        st5_lcvb_v = m.Wire('st5_lcvb_v', n_neighbors)
        st5_dvac = m.Wire('st5_dvac', n_neighbors * dist_bits)
        st5_dvbc = m.Wire('st5_dvbc', n_neighbors * dist_bits)
        st5_pwa = m.Wire('st5_pwa', w_bits)
        st5_pwb = m.Wire('st5_pwb', w_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st6 output wires
        m.EmbeddedCode('// st6 output wires')
        st6_idx = m.Wire('st6_idx', t_bits)
        st6_v = m.Wire('st6_v')
        st6_dvac = m.Wire('st6_dvac', n_neighbors // 2 * dist_bits)
        st6_dvbc = m.Wire('st6_dvbc', n_neighbors // 2 * dist_bits)
        st6_dvas = m.Wire('st6_dvas', n_neighbors * dist_bits)
        st6_dvbs = m.Wire('st6_dvbs', n_neighbors * dist_bits)
        st6_pwa = m.Wire('st6_pwa', w_bits)
        st6_pwb = m.Wire('st6_pwb', w_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st7 output wires
        m.EmbeddedCode('// st7 output wires')
        st7_idx = m.Wire('st7_idx', t_bits)
        st7_v = m.Wire('st7_v')
        st7_dvac = m.Wire('st7_dvac', dist_bits)
        st7_dvbc = m.Wire('st7_dvbc', dist_bits)
        st7_dvas = m.Wire('st7_dvas', n_neighbors // 2 * dist_bits)
        st7_dvbs = m.Wire('st7_dvbs', n_neighbors // 2 * dist_bits)
        st7_pwa = m.Wire('st7_pwa', w_bits)
        st7_pwb = m.Wire('st7_pwb', w_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st8 output wires
        m.EmbeddedCode('// st8 output wires')
        st8_idx = m.Wire('st8_idx', t_bits)
        st8_v = m.Wire('st8_v')
        st8_dc = m.Wire('st8_dc', dist_bits)
        st8_dvas = m.Wire('st8_dvas', dist_bits)
        st8_dvbs = m.Wire('st8_dvbs', dist_bits)
        st8_pwa = m.Wire('st8_pwa', w_bits)
        st8_pwb = m.Wire('st8_pwb', w_bits)

        # st9 output wires
        m.EmbeddedCode('// st9 output wires')
        st9_idx = m.Wire('st9_idx', t_bits)
        st9_v = m.Wire('st9_v')
        st9_dc = m.Wire('st9_dc', dist_bits)
        st9_ds = m.Wire('st9_ds', dist_bits)
        st9_pwa = m.Wire('st9_pwa', w_bits)
        st9_pwb = m.Wire('st9_pwb', w_bits)
        m.EmbeddedCode('// -----')
        # -----

        # st10 output wires
        m.EmbeddedCode('// st10 output wires')
        st10_idx = m.Wire('st10_idx', t_bits)
        st10_v = m.Wire('st10_v')
        st10_sw = m.Wire('st10_sw')
        st10_wa = m.Wire('st10_wa', w_bits)
        st10_wb = m.Wire('st10_wb', w_bits)
        m.EmbeddedCode('// -----')
        # -----

        # modules instantiations
        par = []
        con = [
            ('clk', clk),
            ('rst', rst),
            ('start', start),
            ('done', done),
            ('idx_out', th_idx),
            ('v_out', th_v),
            ('ca_out', th_ca),
            ('cb_out', th_cb),
        ]
        aux = self.create_threads_controller()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('st1_wr', st1_wr),
            ('st1_wr_addr', st1_wr_addr),
            ('st1_wr_data', st1_wr_data),
            ('rd', rd),
            ('rd_addr', rd_addr),
            ('out_v', out_v),
            ('out_data', out_data),
            ('clk', clk),
            ('rst', rst),
            ('idx_in', th_idx),
            ('v_in', th_v),
            ('ca_in', th_ca),
            ('cb_in', th_cb),
            ('sw_in', st10_sw),
            ('st1_wb_in', st1_wb),
            ('st10_wa_in', st10_wa),
            ('st10_wb_in', st10_wb),
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
            ('wb_out', st1_wb),
            ('pwa_out', st1_pwa),
            ('pwb_out', st1_pwb)
        ]
        aux = self.create_st1_c2n()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('st2_wr', st2_wr),
            ('st2_wr_addr', st2_wr_addr),
            ('st2_wr_data', st2_wr_data),
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
            ('pwa_in', st1_pwa),
            ('pwb_in', st1_pwb),
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
            ('pwa_out', st2_pwa),
            ('pwb_out', st2_pwb)
        ]
        aux = self.create_st2_n()
        m.Instance(aux, aux.name, par, con)

        pa = []
        con = [
            ('st3_wr', st3_wr),
            ('st3_wr_addr', st3_wr_addr),
            ('st3_wr_data', st3_wr_data),
            ('clk', clk),
            ('rst', rst),
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
            ('pwa_in', st2_pwa),
            ('pwb_in', st2_pwb),
            ('idx_out', st3_idx),
            ('v_out', st3_v),
            ('ca_out', st3_ca),
            ('cb_out', st3_cb),
            ('cva_out', st3_cva),
            ('cva_v_out', st3_cva_v),
            ('cvb_out', st3_cvb),
            ('cvb_v_out', st3_cvb_v),
            ('wb_out', st3_wb),
            ('pwa_out', st3_pwa),
            ('pwb_out', st3_pwb)
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
            ('pwa_in', st3_pwa),
            ('pwb_in', st3_pwb),
            ('idx_out', st4_idx),
            ('v_out', st4_v),
            ('lca_out', st4_lca),
            ('lcb_out', st4_lcb),
            ('lcva_out', st4_lcva),
            ('lcva_v_out', st4_lcva_v),
            ('lcvb_out', st4_lcvb),
            ('lcvb_v_out', st4_lcvb_v),
            ('pwa_out', st4_pwa),
            ('pwb_out', st4_pwb)
        ]
        aux = self.create_st4_lcf()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st4_idx),
            ('v_in', st4_v),
            ('lca_in', st4_lca),
            ('lcb_in', st4_lcb),
            ('lcva_in', st4_lcva),
            ('lcva_v_in', st4_lcva_v),
            ('lcvb_in', st4_lcvb),
            ('lcvb_v_in', st4_lcvb_v),
            ('pwa_in', st4_pwa),
            ('pwb_in', st4_pwb),
            ('idx_out', st5_idx),
            ('v_out', st5_v),
            ('lca_out', st5_lca),
            ('lcb_out', st5_lcb),
            ('lcva_out', st5_lcva),
            ('lcva_v_out', st5_lcva_v),
            ('lcvb_out', st5_lcvb),
            ('lcvb_v_out', st5_lcvb_v),
            ('dvac_out', st5_dvac),
            ('dvbc_out', st5_dvbc),
            ('pwa_out', st5_pwa),
            ('pwb_out', st5_pwb),
        ]
        aux = self.create_st5_d1()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st5_idx),
            ('v_in', st5_v),
            ('lca_in', st5_lca),
            ('lcb_in', st5_lcb),
            ('lcva_in', st5_lcva),
            ('lcva_v_in', st5_lcva_v),
            ('lcvb_in', st5_lcvb),
            ('lcvb_v_in', st5_lcvb_v),
            ('dvac_in', st5_dvac),
            ('dvbc_in', st5_dvbc),
            ('pwa_in', st5_pwa),
            ('pwb_in', st5_pwb),
            ('idx_out', st6_idx),
            ('v_out', st6_v),
            ('dvac_out', st6_dvac),
            ('dvbc_out', st6_dvbc),
            ('dvas_out', st6_dvas),
            ('dvbs_out', st6_dvbs),
            ('pwa_out', st6_pwa),
            ('pwb_out', st6_pwb),
        ]
        aux = self.create_st6_d2_s1()
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
            ('pwa_in', st6_pwa),
            ('pwb_in', st6_pwb),
            ('idx_out', st7_idx),
            ('v_out', st7_v),
            ('dvac_out', st7_dvac),
            ('dvbc_out', st7_dvbc),
            ('dvas_out', st7_dvas),
            ('dvbs_out', st7_dvbs),
            ('pwa_out', st7_pwa),
            ('pwb_out', st7_pwb),

        ]
        aux = self.create_st7_s2()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st7_idx),
            ('v_in', st7_v),
            ('dvac_in', st7_dvac),
            ('dvbc_in', st7_dvbc),
            ('dvas_in', st7_dvas),
            ('dvbs_in', st7_dvbs),
            ('pwa_in', st7_pwa),
            ('pwb_in', st7_pwb),
            ('idx_out', st8_idx),
            ('v_out', st8_v),
            ('dc_out', st8_dc),
            ('dvas_out', st8_dvas),
            ('dvbs_out', st8_dvbs),
            ('pwa_out', st8_pwa),
            ('pwb_out', st8_pwb),
        ]
        aux = self.create_st8_s3()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st8_idx),
            ('v_in', st8_v),
            ('dc_in', st8_dc),
            ('dvas_in', st8_dvas),
            ('dvbs_in', st8_dvbs),
            ('pwa_in', st8_pwa),
            ('pwb_in', st8_pwb),
            ('idx_out', st9_idx),
            ('v_out', st9_v),
            ('dc_out', st9_dc),
            ('ds_out', st9_ds),
            ('pwa_out', st9_pwa),
            ('pwb_out', st9_pwb),
        ]
        aux = self.create_st9_s4()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('idx_in', st9_idx),
            ('v_in', st9_v),
            ('dc_in', st9_dc),
            ('ds_in', st9_ds),
            ('pwa_in', st9_pwa),
            ('pwb_in', st9_pwb),
            ('idx_out', st10_idx),
            ('v_out', st10_v),
            ('sw_out', st10_sw)
        ]
        aux = self.create_st10_cmp()
        m.Instance(aux, aux.name, par, con)

        '''
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
        '''
        # -----

        Util.initialize_regs(m)
        self.cache[name] = m
        return m
