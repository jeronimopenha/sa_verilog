import os
import sys
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())


import src.hw.sa_components as sac
import src.hw.testbenches as _t
from src.utils.util import SaGraph

sa_graph = SaGraph('dot/t.dot')
sa_comp = sac.SAComponents(sa_graph=sa_graph, n_threads=6, n_neighbors=4)
test_bench = _t.create_sa_verilog_test_bench(sa_comp)
#sa_comp.create_sa_pipeline().to_verilog('verilog/sa_pipeline.v')
