import src.utils.util as _u
import src.sw.st2 as _st2


class St3:
    """
    Third Pipe from SA_Verilog. This pipe is responsible to bring the neighboor from each node selected in the left pipe in the graph.
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
            'wa': {'idx': 0, 'c': 0, 'n': None},
            'wb': {'idx': 0, 'c': 0, 'n': None},
        }
        self.output = self.output_new.copy()

    def execute(self, st2: _st2.St2):
        # moving forward the ready outputs
        self.output = self.output_new.copy()

        # reading pipe inputs
        self.output_new['idx'] = st2.output['idx']
        self.output_new['v'] = st2.output['v']
        self.output_new['ca'] = st2.output['ca']
        self.output_new['cb'] = st2.output['cb']
        self.output_new['na'] = st2.output['na']
        self.output_new['nb'] = st2.output['nb']
        self.output_new['wa'] = st2.output['wa']
        self.output_new['wb'] = st2.output['wb']

        self.output_new['va'] = [None, None, None, None]
        self.output_new['vb'] = [None, None, None, None]

        na = st2.output['na']
        nb = st2.output['nb']
        if na is not None:
            for i in range(len(self.neighbors[na])):
                self.output_new['va'][i] = self.neighbors[na][i]
        if nb is not None:
            for i in range(len(self.neighbors[nb])):
                self.output_new['vb'][i] = self.neighbors[nb][i]
