from math import ceil, log2, sqrt, pow

import src.utils.util as _util
import src.sw.st9 as _st9


class St1:
    """
    First Pipe from SA_Verilog. This pipe is responsible to generate the values for esach thread.
    """

    def __init__(self, sa_graph: _util.SaGraph, n_threads: int = 10):
        self.sa_graph = sa_graph
        self.n_threads = n_threads
        self.n_cells = sa_graph.n_cells
        self.t_bits = ceil(log2(self.n_threads))
        self.c_bits = ceil(log2(self.n_cells))
        self.mask = int(pow(ceil(sqrt(self.n_cells)), 2))-1
        self.counter = [0 for i in range(self.n_threads)]

        self.ca = [0 for i in range(self.n_threads)]
        self.cb = [0 for i in range(self.n_threads)]
        self.v = [True for i in range(self.n_threads)]
        self.idx = 0

        self.output_new = {
            'ca': [0, 0],
            'cb': [0, 0],
            'v': [True, True],
            'idx': [0, 0]
        }

        self.output = self.output_new.copy()

    def execute(self):
        idx = self.idx
        t_bits = self.t_bits
        c_bits = self.c_bits
        mask = self.mask
        # commit outputs
        self.output = self.output_new.copy()

        # process the new output
        self.idx += 1
        if self.idx == self.n_threads:
            self.idx = 0
        self.v[idx] = not self.v[idx]
        if self.v[idx]:
            self.counter[idx] += 1
            if self.counter[idx] >= pow(self.n_cells, 2):
                self.counter[idx] = 0
            self.ca[idx] = self.counter[idx] & mask
            self.cb[idx] = (self.counter[idx] >> c_bits) & mask
        self.output_new = {
            'ca': [self.ca[idx], self.ca[idx]],
            'cb': [self.cb[idx], self.cb[idx]],
            'v': [self.v[idx], self.v[idx]],
            'idx': [self.idx, self.idx]
        }
