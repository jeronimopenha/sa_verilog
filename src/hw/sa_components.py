from math import ceil, log2, sqrt
from veriloggen import *
from utils import initialize_regs


class SAComponents:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, n_cells: int = 16, n_neighbors: int = 5, align_bits: int = 8):
        self.cache = {}
        self.n_cells = n_cells
        self.n_neighbors = n_neighbors
        self.align_bits = align_bits

    def create_priority_encoder(self):
        name = 'priority_encoder'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        WIDTH = m.Parameter('WIDTH', 4)
        LSB_PRIORITY = m.Parameter('LSB_PRIORITY', "LOW")
        input_unencoded = m.Input('input_unencoded', WIDTH)
        output_valid = m.Output('output_valid', 1)
        output_encoded = m.Output('output_encoded', EmbeddedCode('$clog2(WIDTH)'))
        output_unencoded = m.Output('output_unencoded', WIDTH)

        W1 = m.Localparam('W1', EmbeddedCode('2**$clog2(WIDTH)'))
        W2 = m.Localparam('W2', EmbeddedCode('W1/2'))

        gen_if = m.GenerateIf(WIDTH == 2, 'if_width')
        gen_if.Assign(output_valid(input_unencoded[0] | input_unencoded[1]))
        gen_if2 = gen_if.GenerateIf(LSB_PRIORITY == 'LOW', 'if_low')
        gen_if2.Assign(output_encoded(input_unencoded[1]))
        gen_if2 = gen_if2.Else('else_low')
        gen_if2.EmbeddedCode('assign output_encoded = ~input_unencoded[0];')
        gen_if = gen_if.Else('else_width')
        gen_if.Wire('out1', EmbeddedCode('$clog2(W2)'))
        gen_if.Wire('out2', EmbeddedCode('$clog2(W2)'))
        gen_if.Wire('valid1')
        gen_if.Wire('valid2')
        gen_if.Wire('out_un', WIDTH)
        gen_if.EmbeddedCode('priority_encoder #(\n\
                    .WIDTH(W2),\n\
                    .LSB_PRIORITY(LSB_PRIORITY)\n\
                )\n\
                priority_encoder_inst1 (\n\
                    .input_unencoded(input_unencoded[W2-1:0]),\n\
                    .output_valid(valid1),\n\
                    .output_encoded(out1),\n\
                    .output_unencoded(out_un[W2-1:0])\n\
                );\n\
                priority_encoder #(\n\
                    .WIDTH(W2),\n\
                    .LSB_PRIORITY(LSB_PRIORITY)\n\
                )\n\
                priority_encoder_inst2 (\n\
                    .input_unencoded({{W1-WIDTH{1\'b0}}, input_unencoded[WIDTH-1:W2]}),\n\
                    .output_valid(valid2),\n\
                    .output_encoded(out2),\n\
                    .output_unencoded(out_un[WIDTH-1:W2])\n\
                );')
        gen_if.EmbeddedCode('       assign output_valid = valid1 | valid2;\n\
                if (LSB_PRIORITY == "LOW") begin\n\
                    assign output_encoded = valid2 ? {1\'b1, out2} : {1\'b0, out1};\n\
                end else begin\n\
                    assign output_encoded = valid1 ? {1\'b0, out1} : {1\'b1, out2};\n\
                end')
        m.EmbeddedCode('assign output_unencoded = 1 << output_encoded;')

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_arbiter(self):
        name = 'arbiter'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        PORTS = m.Parameter('PORTS', 4)
        TYPE = m.Parameter('TYPE', "ROUND_ROBIN")
        BLOCK = m.Parameter('BLOCK', "NONE")
        LSB_PRIORITY = m.Parameter('LSB_PRIORITY', "LOW")
        clk = m.Input('clk')
        rst = m.Input('rst')
        request = m.Input('request', PORTS)
        acknowledge = m.Input('acknowledge', PORTS)
        grant = m.Output('grant', PORTS)
        grant_valid = m.Output('grant_valid')
        grant_encoded = m.Output('grant_encoded', EmbeddedCode('$clog2(PORTS)'))

        grant_reg = m.Reg('grant_reg', PORTS)
        grant_next = m.Reg('grant_next', PORTS)
        grant_valid_reg = m.Reg('grant_valid_reg')
        grant_valid_next = m.Reg('grant_valid_next')
        grant_encoded_reg = m.Reg('grant_encoded_reg', EmbeddedCode('$clog2(PORTS)'))
        grant_encoded_next = m.Reg('grant_encoded_next', EmbeddedCode('$clog2(PORTS)'))

        m.Assign(grant_valid(grant_valid_reg))
        m.Assign(grant(grant_reg))
        m.Assign(grant_encoded(grant_encoded_reg))

        request_valid = m.Wire('request_valid')
        request_index = m.Wire('request_index', EmbeddedCode('$clog2(PORTS)'))
        request_mask = m.Wire('request_mask', PORTS)

        pe = self.create_priority_encoder()
        params = [('WIDTH', PORTS), ('LSB_PRIORITY', LSB_PRIORITY)]
        con = [
            ('input_unencoded', request),
            ('output_valid', request_valid),
            ('output_encoded', request_index),
            ('output_unencoded', request_mask)
        ]
        m.Instance(pe, 'priority_encoder_inst', params, con)
        mask_reg = m.Reg('mask_reg', PORTS)
        mask_next = m.Reg('mask_next', PORTS)
        masked_request_valid = m.Wire('masked_request_valid')
        masked_request_index = m.Wire('masked_request_index', EmbeddedCode('$clog2(PORTS)'))
        masked_request_mask = m.Wire('masked_request_mask', PORTS)
        params = [('WIDTH', PORTS), ('LSB_PRIORITY', LSB_PRIORITY)]
        con = [
            ('input_unencoded', request & mask_reg),
            ('output_valid', masked_request_valid),
            ('output_encoded', masked_request_index),
            ('output_unencoded', masked_request_mask)
        ]
        m.Instance(pe, 'priority_encoder_masked', params, con)

        m.Always()(
            grant_next(0, blk=True),
            grant_valid_next(0, blk=True),
            grant_encoded_next(0, blk=True),
            mask_next(mask_reg, blk=True),
            If(AndList(BLOCK == "REQUEST", grant_reg & request))(
                grant_valid_next(grant_valid_reg, blk=True),
                grant_next(grant_reg, blk=True),
                grant_encoded_next(grant_encoded_reg, blk=True)
            ).Elif(AndList(BLOCK == "ACKNOWLEDGE", grant_valid, Not(grant_reg & acknowledge)))(
                grant_valid_next(grant_valid_reg, blk=True),
                grant_next(grant_reg, blk=True),
                grant_encoded_next(grant_encoded_reg, blk=True)
            ).Elif(request_valid)(
                If(TYPE == "PRIORITY")(
                    grant_valid_next(1, blk=True),
                    grant_next(request_mask, blk=True),
                    grant_encoded_next(request_index, blk=True)
                ).Elif(TYPE == "ROUND_ROBIN")(
                    If(masked_request_valid)(
                        grant_valid_next(1, blk=True),
                        grant_next(masked_request_mask, blk=True),
                        grant_encoded_next(masked_request_index, blk=True),
                        If(LSB_PRIORITY == "LOW")(
                            EmbeddedCode('mask_next = {PORTS{1\'b1}} >> (PORTS - masked_request_index);')
                        ).Else(
                            EmbeddedCode('mask_next = {PORTS{1\'b1}} << (masked_request_index + 1);')
                        )
                    ).Else(
                        grant_valid_next(1, blk=True),
                        grant_next(request_mask, blk=True),
                        grant_encoded_next(request_index, blk=True),
                        If(LSB_PRIORITY == "LOW")(
                            EmbeddedCode('mask_next = {PORTS{1\'b1}} >> (PORTS - request_index);')
                        ).Else(
                            EmbeddedCode('mask_next = {PORTS{1\'b1}} << (request_index + 1);')
                        )
                    )
                )

            )
        )
        m.Always(Posedge(clk))(
            If(rst)(
                grant_reg(0),
                grant_valid_reg(0),
                grant_encoded_reg(0),
                mask_reg(0)
            ).Else(
                grant_reg(grant_next),
                grant_valid_reg(grant_valid_next),
                grant_encoded_reg(grant_encoded_next),
                mask_reg(mask_next)
            )
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_thread(self):
        n_cells = self.n_cells
        name = 'thread_%d_cells' % n_cells
        if name in self.cache.keys():
            return self.cache[name]

        bits = ceil(log2(n_cells))
        m = Module(name)

        clk = m.Input('clk')
        rst = m.Input('rst')
        done = m.OutputReg('done')

        cell_n = m.Input('cell_n')
        cell_r = m.Input('cell_r')
        cell_v = m.OutputReg('cell_v')
        cell1 = m.Output('cell1', bits)
        cell2 = m.Output('cell2', bits)

        counter = m.Reg('counter', (bits*2) + 1)

        cell1.assign(counter[0:cell1.width])
        cell2.assign(counter[cell2.width:counter.width-1])

        fsm_thread = m.Reg('fsm_thread', 3)
        FSM_VERIFY_EQ = m.Localparam('FSM_VERIFY_EQ', 0)
        FSM_WAIT_READ_CELLS = m.Localparam('FSM_WAIT_READ_CELLS', 1)
        FSM_WAIT_NEXT_CELL = m.Localparam('FSM_WAIT_NEXT_CELL', 2)
        FSM_DONE = m.Localparam('FSM_DONE', 3)
        FSM_VERIFY_DONE = m.Localparam('FSM_VERIFY_DONE', 4)

        m.Always(Posedge(clk))(
            If(rst)(
                cell_v(0),
                counter(1),
                fsm_thread(FSM_VERIFY_EQ),
            ).Else(
                Case(fsm_thread)(
                    When(FSM_VERIFY_EQ)(
                        If(cell1 == cell2)(
                            counter.inc(),
                        ).Else(
                            cell_v(1),
                            fsm_thread(FSM_WAIT_READ_CELLS)
                        )
                    ),
                    When(FSM_WAIT_READ_CELLS)(
                        If(cell_r)(
                            cell_v(0),
                            fsm_thread(FSM_WAIT_NEXT_CELL)
                        )
                    ),
                    When(FSM_WAIT_NEXT_CELL)(
                        If(cell_n)(
                            fsm_thread(FSM_VERIFY_DONE)
                        )
                    ),
                    When(FSM_VERIFY_DONE)(
                        If(counter == (n_cells*n_cells)-1)(
                            fsm_thread(FSM_DONE),
                        ).Else(
                            counter.inc(),
                            fsm_thread(FSM_VERIFY_EQ)
                        )
                    ),
                    When(FSM_DONE)(
                        done(1),
                    )
                )
            )
        )
        initialize_regs(m)

        self.cache[name] = m
        return m


comp = SAComponents()
comp.create_thread().to_verilog('thread.v')
comp.create_arbiter().to_verilog('arbiter.v')
