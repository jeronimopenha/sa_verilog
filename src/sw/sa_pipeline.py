import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import st1 as _st1
import st2 as _st2
import st3 as _st3
import st4 as _st4
import src.utils.util as _u


if __name__ == '__main__':
    n_threads = 2
    sa_graph = _u.SaGraph('dot/t.dot')
    st1 = _st1.St1(sa_graph, n_threads=n_threads)
    st2 = _st2.St2(sa_graph, n_threads=n_threads)
    st3 = _st3.St3(sa_graph)
    st4 = _st4.St4(sa_graph, n_threads=n_threads)

    for i in range(64):
        st1.execute()
        # print(st1.output)
        st2.execute(st1, None)
        # print(st2.output)
        st3.execute(st2)
        #
        st4.execute(st3)
