import src.utils.util as _u


class St4:
    """
    Fourth Pipe from SA_Verilog. This pipe is responsible to bring the neighboor's cell from each neighbor node.
    """

    def __init__(self, sa_graph: _u.SaGraph, n_threads: int = 10):
        self.sa_graph = sa_graph
        self.sa_graph.reset_random()
        self.n_threads = n_threads
        self.n2c = [sa_graph.get_initial_grid()[1]
                    for i in range(self.n_threads)]

        self.output_new = {
            'idx': 0,
            'v': False,
            'ca': 0,
            'cb': 0,
            'cva': [None, None, None, None],
            'cvb': [None, None, None, None],
            'wa': {'idx': 0, 'c': 0, 'n': None},
            'wb': {'idx': 0, 'c': 0, 'n': None},
        }
        self.output = self.output_new.copy()

    def execute(self, _in: dict()):
        # moving forward the ready outputs
        self.output = self.output_new.copy()

        # reading pipe inputs
        self.output_new['idx'] = _in['idx']
        self.output_new['v'] = _in['v']
        self.output_new['ca'] = _in['ca']
        self.output_new['cb'] = _in['cb']
        self.output_new['wa'] = _in['wa']
        self.output_new['wb'] = _in['wb']

        self.output_new['cva'] = [None, None, None, None]
        self.output_new['cvb'] = [None, None, None, None]

        idx = _in['idx']
        va = _in['va']
        vb = _in['vb']

        for i in range(len(va)):
            if va[i] is not None:
                self.output_new['cva'][i] = self.n2c[idx][va[i]]
            else:
                break
        for i in range(len(vb)):
            if vb[i] is not None:
                self.output_new['cvb'][i] = self.n2c[idx][vb[i]]
            else:
                break
