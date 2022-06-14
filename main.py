import os
import sys
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())
from src.sw.sa import sa

sa('dot/simple.dot',1,2)