class St9:
    """
    Eighth Pipe from SA_Verilog. This pipe is responsible to execute the 2-2 
    additions for the distances found in the left pipe.
    """

    def __init__(self):
        self.output_new = {
            'idx': 0,
            'v': False,
            'dc': 0,
            'ds': 0
        }
        self.output = self.output_new.copy()

    def execute(self, _in: dict()):
        # moving forward the ready outputs
        self.output = self.output_new.copy()

        self.output_new['idx'] = _in['idx']
        self.output_new['v'] = _in['v']

        dc = _in['dc']
        dvas = _in['dvas']
        dvbs = _in['dvbs']

        self.output_new['dc'] = _in['dc']
        self.output_new['ds'] = dvas + dvbs
        
