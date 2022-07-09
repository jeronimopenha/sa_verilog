class St6:
    """
    Sixth Pipe from SA_Verilog. This pipe is responsible to execute the 2-2 
    additions for the distances found in the left pipe.
    """

    def __init__(self):
        self.output_new = {
            'idx': 0,
            'v': False,
            'dvac': 0,
            'dvbc': 0,
            'dvas': [0, 0],
            'dvbs': [0, 0]
        }
        self.output = self.output_new.copy()

    def execute(self, _in: dict()):
        # moving forward the ready outputs
        self.output = self.output_new.copy()

        self.output_new['idx'] = _in['idx']
        self.output_new['v'] = _in['v']

        dvac = _in['dvac']
        dvbc = _in['dvbc']
        dvas = _in['dvas']
        dvbs = _in['dvbs']

        self.output_new['dvac'] = dvac[0] + dvac[1]
        self.output_new['dvbc'] = dvbc[0] + dvbc[1]
        self.output_new['dvas'] = [dvas[0] + dvas[1], dvas[2] + dvas[3]]
        self.output_new['dvbs'] = [dvbs[0] + dvbs[1], dvbs[2] + dvbs[3]]
