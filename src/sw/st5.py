import src.utils.util as _u


class St5:
    """
    Fifth Pipe from SA_Verilog. This pipe is responsible to find the manhatan 
    distances for each combination between cellA and cellB with their 
    respective neighboors cells after swap and execute the first 2-2 additions 
    for the distances found in the left pipe.
    """

    def __init__(self, sa_graph: _u.SaGraph):
        self.sa_graph = sa_graph
        self.output_new = {
            'idx': 0,
            'v': False,
            'dvac': [0, 0],
            'dvbc': [0, 0],
            'dvas': [0, 0, 0, 0],
            'dvbs': [0, 0, 0, 0]
        }
        self.output = self.output_new.copy()

    def execute(self, _in: dict()):
        # moving forward the ready outputs
        self.output = self.output_new.copy()

        self.output_new['idx'] = _in['idx']
        self.output_new['v'] = _in['v']

        cbs = _in['ca']
        cas = _in['cb']
        cva = _in['cva']
        cvb = _in['cvb']
        dvac = _in['dvac']
        dvbc = _in['dvbc']

        self.output_new['dvac'] = [dvac[0] + dvac[1], dvac[2] + dvac[3]]
        self.output_new['dvbc'] = [dvbc[0] + dvbc[1], dvbc[2] + dvbc[3]]

        self.output_new['dvas'] = [0, 0, 0, 0]
        self.output_new['dvbs'] = [0, 0, 0, 0]

        for i in range(len(cva)):
            if cva[i] is not None:
                if cas == cva[i]:
                    self.output_new['dvas'][i] = self.sa_graph.get_manhattan_distance(
                        cas, cbs)
                else:
                    self.output_new['dvas'][i] = self.sa_graph.get_manhattan_distance(
                        cas, cva[i])
            else:
                break

        for i in range(len(cvb)):
            if cvb[i] is not None:
                if cbs == cvb[i]:
                    self.output_new['dvbs'][i] = self.sa_graph.get_manhattan_distance(
                        cas, cbs)
                else:
                    self.output_new['dvbs'][i] = self.sa_graph.get_manhattan_distance(
                        cbs, cvb[i])
            else:
                break
