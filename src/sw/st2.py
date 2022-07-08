import src.sw.st1 as _st1
import src.utils.util as _u


class St2:
    """
    Second Pipe from SA_Verilog. This pipe is responsible to search the content of the two cells selected by threads
    """

    def __init__(self, sa_graph: _u.SaGraph, n_threads: int = 10):
        self.sa_graph = sa_graph
        self.sa_graph.reset_random()
        self.n_threads = n_threads
        self.c2n = [sa_graph.get_initial_grid()[0]
                    for i in range(self.n_threads)]
        self.fifo_a = [{'idx': 0, 'c': 0, 'n': None}
                       for i in range(self.n_threads)]
        self.fifo_b = [{'idx': 0, 'c': 0, 'n': None}
                       for i in range(self.n_threads)]

        self.output_new = {
            'idx': 0,
            'v': False,
            'ca': 0,
            'cb': 0,
            'na': None,
            'nb': None,
            'wa': {'idx': 0, 'c': 0, 'n': None},
            'wb': {'idx': 0, 'c': 0, 'n': None},
        }
        self.output = self.output_new.copy()

    # TODO update logic
    def execute(self, st1: _st1.St1, st9):
        # enqueuing data
        self.fifo_a.append(
            {'idx': self.output_new['idx'], 'c': self.output_new['ca'], 'n': self.output_new['na']})
        self.fifo_b.append(
            {'idx': self.output_new['idx'], 'c': self.output_new['ca'], 'n': self.output_new['nb']})

        # moving forward the ready outputs
        self.output = self.output_new.copy()

        # reading pipe inputs
        idx = st1.output['idx']
        v = st1.output['v']
        ca = st1.output['ca']
        cb = st1.output['cb']

        # data ready to be moved forward
        self.output_new['idx'] = idx
        self.output_new['v'] = v
        self.output_new['ca'] = ca
        self.output_new['cb'] = cb

        # cell content ready to be moved forward
        self.output_new['na'] = self.c2n[idx][ca]
        self.output_new['nb'] = self.c2n[idx][cb]

        # Pop Queues
        wa = {'idx': 0, 'c': 0, 'n': None}
        wb = {'idx': 0, 'c': 0, 'n': None}
        if v:
            wa = self.fifo_a.pop()
            wb = self.fifo_b.pop()

        # fifos outptuts ready to be moved forward
        self.output_new['wa'] = wa
        self.output_new['wb'] = wb

        # TODO update table
