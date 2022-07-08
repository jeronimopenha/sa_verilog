import src.utils.util as _u
import src.sw.st3 as _st3


class St4:
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
            'na': None,
            'nb': None,
            'va': [None, None, None, None],
            'vb': [None, None, None, None],
            'cva': [None, None, None, None],
            'cvb': [None, None, None, None],
            'wa': {'idx': 0, 'c': 0, 'n': None},
            'wb': {'idx': 0, 'c': 0, 'n': None},
        }
        self.output = self.output_new.copy()

    def execute(self, st3: _st3.St3):
        # moving forward the ready outputs
        self.output = self.output_new.copy()

        # reading pipe inputs
        self.output_new['idx'] = st3.output['idx']
        self.output_new['v'] = st3.output['v']
        self.output_new['ca'] = st3.output['ca']
        self.output_new['cb'] = st3.output['cb']
        self.output_new['na'] = st3.output['na']
        self.output_new['nb'] = st3.output['nb']
        self.output_new['wa'] = st3.output['wa']
        self.output_new['wb'] = st3.output['wb']
        self.output_new['va'] = st3.output['va']
        self.output_new['vb'] = st3.output['vb']

        self.output_new['cva'] = [None, None, None, None]
        self.output_new['cvb'] = [None, None, None, None]

        idx = st3.output['idx']
        va = st3.output['va']
        vb = st3.output['vb']

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
