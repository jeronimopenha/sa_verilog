from math import ceil, log2
import src.sw.st1 as _st1

from src.utils.util import SaGraph


class St2:
    """
    Second Pipe from SA_Verilog. This pipe is responsible to search the content of the two cells selected by threads
    """

    def __init__(self, sa_graph: SaGraph, n_threads: int = 10):
        self.sa_graph = sa_graph
        self.sa_graph.reset_random()
        self.n_threads = n_threads
        self.c2n = [sa_graph.get_initial_grid()[0]
                    for i in range(self.n_threads)]
        self.fifo_a = [{'c': 0, 'n': None}
                       for i in range(self.n_threads)]
        self.fifo_b = [{'c': 0, 'n': None}
                       for i in range(self.n_threads)]
        self.fifo_idx = [0 for i in range(self.n_threads)]

        self.output = {
            'ca': [0, 0],
            'cb': [0, 0],
            'v': False,
            'idx': 0,
            'w_a': {'c': 0, 'n': None},
            'w_b': {'c': 0, 'n': None},
            'w_idx': 0,
            'na': None,
            'nav': False,
            'nb': 0,
            'nbv': False
        }
        self.output_new = self.output.copy()

    # bus = fanout 2
    # wire = fanout 4
    def execute(self, st1: _st1.St1, st9):
        # reading pipe inputs
        idx = st1.output['idx']
        ca = st1.output['ca']
        cb = st1.output['cb']
        v = st1.output['v']

        # node 2 cell area
        na = self.c2n[idx][0][ca]
        nb = self.c2n[idx][0][ca]
        # ----

        # Queue area
        # POP Queues
        wa = {'idx': 0, 'c': 0, 'n': None}
        wb = {'idx': 0, 'c': 0, 'n': None}
        if v[0]:  # 1
            wa = self.fifo_a.pop()
        if v[0]:  # 2
            wb = self.fifo_b.pop()
        # enqueuing data
        self.fifo_a.append({'c': 0, 'n': None})
        self.fifo_a.append({'c': 0, 'n': None})
        self.fifo_idx.append(self.output_new['idx'])

        # node 2 cell area

        # ----

        # repassing queues data area
        self.output_new['wa'] = wa
        self.output_new['wb'] = wb
        # ----

        # repassing data
        self.output_new['ca'] = [ca[1]for i in range(self.output_new['ca'])]
        self.output_new['cb'] = [cb[1]for i in range(self.output_new['ca'])]
        '''self.output = {
            'ca': [0 for i in range(2)],
            'cb': [0 for i in range(2)],
            'v': False,
            'idx': 0,
            'w_a': [],
            'w_b': [],
            'na': None,
            'nav': False,
            'nb': 0,
            'nbv': False
        }
        '''

        # FIXME - Implementar a atualização

    def commit(self):
        self.output = self.output_new.copy()
