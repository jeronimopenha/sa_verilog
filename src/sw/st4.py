import src.utils.util as _u


class St4:
    """
    Fourth Pipe from SA_Verilog. This pipe is responsible to find the manhatan 
    distances for each combination between cellA and cellB with their 
    respective neighboors cells before swap.
    """

    def __init__(self, sa_graph: _u.SaGraph):
        self.sa_graph = sa_graph
        self.output_new = {
            'idx': 0,
            'v': False,
            'ca': 0,
            'cb': 0,
            'cva': [None, None, None, None],
            'cvb': [None, None, None, None],
            'dvac': [0, 0, 0, 0],
            'dvbc': [0, 0, 0, 0]
        }
        self.output = self.output_new.copy()

    def execute(self, _in: dict()):
        # moving forward the ready outputs
        self.output = self.output_new.copy()

        self.output_new['idx'] = _in['idx']
        self.output_new['v'] = _in['v']
        self.output_new['ca'] = _in['ca']
        self.output_new['cb'] = _in['cb']
        self.output_new['cva'] = _in['cva']
        self.output_new['cvb'] = _in['cvb']

        self.output_new['dvac'] = [0, 0, 0, 0]
        self.output_new['dvbc'] = [0, 0, 0, 0]

        ca = _in['ca']
        cb = _in['cb']
        cva = _in['cva']
        cvb = _in['cvb']

        for i in range(len(cva)):
            if cva[i] is not None:
                self.output_new['dvac'][i] = self.sa_graph.get_manhattan_distance(
                    ca, cva[i])
            else:
                break

        for i in range(len(cvb)):
            if cvb[i] is not None:
                self.output_new['dvbc'][i] = self.sa_graph.get_manhattan_distance(
                    cb, cvb[i])
            else:
                break
