import os
import sys
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
#from src.sw.sa_ant import sa
#from src.hw.testbenches0 import create_sa_test_bench
#from src.hw.antigo1 import SAComponents
import src.hw.sa_components as sac
from src.utils.util import SaGraph

sa_graph = SaGraph('dot/t.dot')
sa_comp = sac.SAComponents(sa_graph=sa_graph, n_threads=5, n_neighbors=4)
sa_comp.create_sa_pipeline().to_verilog('verilog/sa_pipeline.v')
