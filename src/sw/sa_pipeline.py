import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import st1 as _st1
import st2 as _st2
import src.utils.util as _util


if __name__ == '__main__':
    n_threads = 2
    sa_graph = _util.SaGraph('dot/t.dot')
    st1 = _st1.St1(sa_graph, n_threads=n_threads)
    st2 = _st2.St2(sa_graph, n_threads=n_threads)

    for i in range(64):
        st1.execute()
        st2.execute(st1, None)
        #print('th:%d a - ' % st1.idx)
        # print(st1.output)
