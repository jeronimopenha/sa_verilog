import os
from math import ceil, log2, sqrt
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

    # TODO I just developed only the interface for now
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
        d_width = ceil(log2(lines+columns))
        d_width += ceil(log2(n_neighbors))

        m = Module(name)
        clk = m.Input('clk')

        # interface
        idx_in = m.Input('idx_in', t_bits)
        v_in = m.Input('v_in')
        ca_in = m.Input('ca_in', c_bits)
        cb_in = m.Input('cb_in', c_bits)
        sw_in = m.Input('sw_in')
        wb_in = m.Input('wb_in', t_bits+c_bits+node_bits)

        idx_out = m.OutputReg('idx_out', t_bits)
        v_out = m.OutputReg('v_out')
        ca_out = m.OutputReg('ca_out', c_bits)
        cb_out = m.OutputReg('cb_out', c_bits)
        na_out = m.OutputReg('na_out', node_bits)
        na_v_out = m.OutputReg('na_v_out')
        nb_out = m.OutputReg('nb_out', node_bits)
        nb_v_out = m.OutputReg('nb_v_out')
        sw_out = m.OutputReg('sw_out')
        wa_out = m.OutputReg('wa_out', t_bits+c_bits+node_bits)
        wb_out = m.OutputReg('wb_out', t_bits+c_bits+node_bits)
        # -----

        initialize_regs(m)
        self.cache[name] = m
        return m

    # TODO I just develop only the interface for now
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
        d_width = ceil(log2(lines+columns))
        d_width += ceil(log2(n_neighbors))

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
        wa_in = m.Input('wa_in', t_bits+c_bits+node_bits)
        wb_in = m.Input('wb_in', t_bits+c_bits+node_bits)

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
        wa_out = m.OutputReg('wa_out', t_bits+c_bits+node_bits)
        wb_out = m.OutputReg('wb_out', t_bits+c_bits+node_bits)

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
        d_width = ceil(log2(lines+columns))
        d_width += ceil(log2(n_neighbors))

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
        st1_wa = m.Wire('st1_wa', t_bits+c_bits+node_bits)
        st1_wb = m.Wire('st1_wb', t_bits+c_bits+node_bits)
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
        st2_wa = m.Wire('st2_wa', t_bits+c_bits+node_bits)
        st2_wb = m.Wire('st2_wb', t_bits+c_bits+node_bits)

        m.EmbeddedCode('// -----')
        # -----

        # st10 output wires
        m.EmbeddedCode('// st10 output wires')
        st10_sw = m.Wire('st10_sw')
        m.EmbeddedCode('// -----')
        # -----

        # modules instantiations
        par = []
        con = [
            ('clk', clk),
            ('idx_in',      th_idx),
            ('v_in',        th_v),
            ('ca_in',       th_ca),
            ('cb_in',       th_cb),

            ('sw_in',       st10_sw),
            ('wb_in',       st1_wb),

            ('idx_out',     st1_idx),
            ('v_out',       st1_v),
            ('ca_out',      st1_ca),
            ('cb_out',      st1_cb),
            ('na_out',      st1_na),
            ('na_v_out',    st1_na_v),
            ('nb_out',      st1_nb),
            ('nb_v_out',    st1_nb_v),
            ('sw_out',      st1_sw),
            ('wa_out',      st1_wa),
            ('wb_out',      st1_wb)
        ]
        aux = self.create_st1_c2n()
        m.Instance(aux, aux.name, par, con)

        par = []
        con = [
            ('idx_in', ),
            ('v_in'),
            ('ca_in', ),
            ('cb_in', ),
            ('na_in', ),
            ('na_v_in'),
            ('nb_in', ),
            ('nb_v_in'),
            ('sw_in'),
            ('wa_in', ),
            ('wb_in', ),
            
            ('idx_out', ),
            ('v_out'),
            ('ca_out', ),
            ('cb_out', ),
            ('na_out', ),
            ('na_v_out'),
            ('nb_out', ),
            ('nb_v_out'),
            ('va_out', ),
            ('va_v_out', ),
            ('vb_out', ),
            ('vb_v_out', ),
            ('sw_out'),
            ('wa_out', ),
            ('wb_out', ),
        ]
        # -----

        initialize_regs(m)
        self.cache[name] = m
        return m
