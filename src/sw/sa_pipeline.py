import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import st1 as _st1
import st2 as _st2
import st3 as _st3
import st4 as _st4
import st5 as _st5
import st6 as _st6
import st7 as _st7
import st8 as _st8
import st9 as _st9
import st10 as _st10
import src.utils.util as _u


if __name__ == '__main__':
    n_threads = 11
    sa_graph = _u.SaGraph('dot/t.dot')
    st1 = _st1.St1(sa_graph, n_threads=n_threads)
    st2 = _st2.St2(sa_graph, n_threads=n_threads)
    st3 = _st3.St3(sa_graph)
    st4 = _st4.St4(sa_graph, n_threads=n_threads)
    st5 = _st5.St5(sa_graph)
    st6 = _st6.St6(sa_graph)
    st7 = _st7.St7()
    st8 = _st8.St8()
    st9 = _st9.St9()
    st10 = _st10.St10()

    for i in range(64):
        st1.execute()
        st2.execute(st1.output, st10.output)
        st3.execute(st2.output)
        st4.execute(st3.output)
        st5.execute(st4.output)
        st6.execute(st5.output)
        st7.execute(st6.output)
        st8.execute(st7.output)
        st9.execute(st8.output)
        st10.execute(st9.output)
        
