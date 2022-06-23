import os
import sys
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
from src.sw.sa import sa
#from src.hw import testbenches
from src.hw.sa_components import SAComponents
from src.utils import util

#sa('dot/simple.dot',1,0.0001)
#sa('dot/simple.dot',1,0.01)
sa_graph = util.SaGraph('dot/t.dot')
sa_comp = SAComponents(sa_graph)
sa_comp.create_sa().to_verilog('sa.v')