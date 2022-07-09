class St9:
    """
    Ninth Pipe from SA_Verilog. This pipe is responsible to take the decision to do the swap or not.
    """

    def __init__(self):
        self.output_new = {
            'idx': 0,
            'v': False,
            'sw': False
        }
        self.output = self.output_new.copy()

    def execute(self, _in: dict()):
        # moving forward the ready outputs
        self.output = self.output_new.copy()

        self.output_new['idx'] = _in['idx']
        self.output_new['v'] = _in['v']

        dc = _in['dc']
        ds = _in['ds']

        self.output_new['sw'] = ds < dc
