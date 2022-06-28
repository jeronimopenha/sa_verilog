from math import ceil, log2, sqrt, pow
from types import new_class


class St1:
    def __init__(self, n_threads: int = 10, n_cells: int = 4):
        self.n_threads = n_threads
        self.n_cells = n_cells
        self.t_bits = ceil(log2(self.n_threads))
        self.c_bits = ceil(log2(self.n_cells))
        self.mask = int(pow(ceil(sqrt(self.n_cells)), 2))-1
        self.init = [True for i in range(self.n_threads)]
        self.counter = [0 for i in range(self.n_threads)]

        self.ca = [0 for i in range(self.n_threads)]
        self.cb = [0 for i in range(self.n_threads)]
        self.v = [False for i in range(self.n_threads)]
        self.idx = 0

        self.output = {
            'ca': 0,
            'cb': 0,
            'v': False,
            'idx': 0
        }

    def execute(self):
        idx = self.idx
        t_bits = self.t_bits
        c_bits = self.c_bits
        mask = self.mask
        if self.init[idx]:
            self.init[idx] = False
            self.v[idx] = True
            self.idx += 1
            if self.idx == self.n_threads:
                self.idx = 0
            return
        self.v[idx] = not self.v[idx]
        if self.v[idx]:
            return
        self.counter[idx] += 1
        if self.counter[idx] == self.n_cells:
            self.counter[idx] = 0
        self.ca[idx] = self.counter[idx] & mask
        self.cb[idx] = (self.counter[idx] >> c_bits) & mask
        self.idx += 1
        if self.idx == self.n_threads:
            self.idx = 0

    def commit(self):
        idx = self.idx
        self.output = {
            'ca': self.ca[idx],
            'cb': self.cb[idx],
            'v': self.v[idx],
            'idx': idx
        }


class St2:
    def __init__(self):
        pass

    def execute(self, st1: St1):
        pass

    def update_output(self):
        pass


class St3:
    def __init__(self):
        pass

    def execute(self, st2: St2):
        pass

    def update_output(self):
        pass


class St4:
    def __init__(self):
        pass

    def execute(self, st3: St3):
        pass

    def update_output(self):
        pass


class St5:
    def __init__(self):
        pass

    def execute(self, st4: St4):
        pass

    def update_output(self):
        pass


class St6:
    def __init__(self):
        pass

    def execute(self, st5: St5):
        pass

    def update_output(self):
        pass


class St7:
    def __init__(self):
        pass

    def execute(self, st6: St6):
        pass

    def update_output(self):
        pass


class St8:
    def __init__(self):
        pass

    def execute(self, st7: St7):
        pass

    def update_output(self):
        pass


class St9:
    def __init__(self):
        pass

    def execute(self, st8: St8):
        pass

    def update_output(self):
        pass


class St10:
    def __init__(self):
        pass

    def execute(self):
        pass

    def update_output(self):
        pass


st1 = St1(n_threads=2)

for i in range(10):
    print(st1.output)
    st1.execute()
    st1.commit()
