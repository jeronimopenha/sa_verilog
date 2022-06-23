import os
import sys
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
from src.sw.sa import sa
from src.hw.testbenches import create_sa_test_bench
from src.hw.sa_components import SAComponents
from src.utils.util import SaGraph

sa_graph = SaGraph('dot/t.dot')
sa_comp = SAComponents(sa_graph=sa_graph, n_threads=1, n_neighbors=2)
sa(sa_graph, 0.01)
create_sa_test_bench(sa_comp)
