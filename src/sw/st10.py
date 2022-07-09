class St10:
    """
    Tenth Pipe from SA_Verilog. This pipe is responsible to generate a sync delay
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
        self.output_new['sw'] = _in['sw']

        
