import src.utils.util as _u


class St2:
    """
    Second Pipe from SA_Verilog. This pipe is responsible to bring the neighboor from each node selected in the left pipe in the graph.
    """

    def __init__(self, sa_graph: _u.SaGraph):
        self.sa_graph = sa_graph
        self.neighbors = self.sa_graph.neighbors

        self.output_new = {
            'idx': 0,
            'v': False,
            'ca': 0,
            'cb': 0,
            'na': None,
            'nb': None,
            'va': [None, None, None, None],
            'vb': [None, None, None, None],
            'sw': {'idx': 0, 'v': False, 'sw': False},
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
        self.output_new['na'] = _in['na']
        self.output_new['nb'] = _in['nb']
        self.output_new['sw'] = _in['sw']
        self.output_new['wa'] = _in['wa']
        self.output_new['wb'] = _in['wb']

        self.output_new['va'] = [None, None, None, None]
        self.output_new['vb'] = [None, None, None, None]

        na = _in['na']
        nb = _in['nb']
        if na is not None:
            for i in range(len(self.neighbors[na])):
                self.output_new['va'][i] = self.neighbors[na][i]
        if nb is not None:
            for i in range(len(self.neighbors[nb])):
                self.output_new['vb'][i] = self.neighbors[nb][i]
