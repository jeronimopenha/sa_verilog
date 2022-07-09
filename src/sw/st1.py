from math import ceil, sqrt
import src.utils.util as _u


class St1:
    """
    First Pipe from SA_Verilog. This pipe is responsible to search the content of the two cells selected by threads
    """

    def __init__(self, sa_graph: _u.SaGraph, n_threads: int = 10):
        self.sa_graph = sa_graph
        self.sa_graph.reset_random()
        self.n_threads = n_threads
        self.c2n = [sa_graph.get_initial_grid()[0]
                    for i in range(self.n_threads)]
        self.fifo_a = [{'idx': 0, 'c': 0, 'n': None}
                       for i in range(self.n_threads-2)]
        self.fifo_b = [{'idx': 0, 'c': 0, 'n': None}
                       for i in range(self.n_threads-2)]
        self.flag = True

        self.output_new = {
            'idx': 0,
            'v': False,
            'ca': 0,
            'cb': 0,
            'na': None,
            'nb': None,
            'sw': {'idx': 0, 'v': False, 'sw': False},
            'wa': {'idx': 0, 'c': 0, 'n': None},
            'wb': {'idx': 0, 'c': 0, 'n': None},
        }
        self.output = self.output_new.copy()
        # for i in range(self.n_threads):
        self.print_matrix(0)

    # TODO update logic
    def execute(self, _in: dict(), _sw: dict(), _wb: dict()):
        # moving forward the ready outputs
        self.output = self.output_new.copy()

        # reading pipe inputs
        idx = _in['idx']
        v = _in['v']
        ca = _in['ca']
        cb = _in['cb']

        # enqueuing data
        if v:
            self.fifo_a.append(
                {'idx': self.output_new['idx'], 'c': self.output_new['ca'], 'n': self.output_new['nb']})
            self.fifo_b.append(
                {'idx': self.output_new['idx'], 'c': self.output_new['cb'], 'n': self.output_new['na']})

        # Pop Queues
        wa = self.output_new['wa']
        wb = self.output_new['wb']
        if v:
            wa = self.fifo_a.pop(0)
            wb = self.fifo_b.pop(0)

        # update memory
        usw = self.output_new['sw']['sw']
        uwa = self.output_new['wa']
        uwb = _wb
        if usw:
            if self.flag:
                self.c2n[uwa['idx']][uwa['c']] = wa['n']
                self.flag = not self.flag
            else:
                self.c2n[uwb['idx']][uwb['c']] = uwb['n']
                self.flag = not self.flag
                if(uwb['idx'] == 0):
                    self.print_matrix(uwb['idx'])

        # fifos outptuts ready to be moved forward
        self.output_new['wa'] = wa
        self.output_new['wb'] = wb
        self.output_new['sw'] = _sw

        # data ready to be moved forward
        self.output_new['idx'] = idx
        self.output_new['v'] = v
        self.output_new['ca'] = ca
        self.output_new['cb'] = cb

        # cell content ready to be moved forward
        self.output_new['na'] = self.c2n[idx][ca]
        self.output_new['nb'] = self.c2n[idx][cb]

    def print_matrix(self, idx: int):
        sqrt_ = ceil(sqrt(len(self.c2n[idx])))
        cidx = 0
        str_ = 'th:%d\n' % idx
        for i in range(sqrt_):
            for j in range(sqrt_):
                str_ += '%d ' % self.c2n[idx][cidx]
                cidx += 1
            str_ += '\n'
        print(str_)
