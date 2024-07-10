import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import src.hw.sa_components_hor as sac
import src.hw.testbenches as _t
from src.utils.sa_graph import SaGraph


sa_graph = SaGraph('dot/mac.dot')

sa_comp = sac.SASaComponentsHor(sa_graph=sa_graph, n_threads=6, n_neighbors=4)
#sa_comp.create_st1_c2n().to_verilog('st1.v')
test_bench = _t.create_sa_pipeline_test_bench(sa_comp)
