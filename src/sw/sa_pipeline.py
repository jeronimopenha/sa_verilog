import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.sw.st1 import St1
from src.sw.st2 import St2
from src.utils.util import SaGraph


if __name__ == '__main__':
    n_threads = 2
    sa_graph = SaGraph('dot/t.dot')
    st1 = St1(sa_graph, n_threads=n_threads)
    #st2 = St2(sa_graph, n_threads=n_threads)

    for i in range(64):
        print('th:%d a - ' % st1.idx)
        print(st1.output)
        st1.execute()
        st1.commit()
