import os
import sys
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
from src.sw.sa import sa
from src.hw import testbenches

#sa('dot/simple.dot',1,0.0001)
#sa('dot/simple.dot',1,0.01)
testbenches.create_threads_test_bench('dot/simple.dot')