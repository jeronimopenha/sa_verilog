from veriloggen import *
import src.hw.sa_components as _sa
import src.utils.util as _u
from math import ceil, log2, sqrt


class SaAws:

    def get(self, sa_graph: _u.SaGraph, bus_width):
        self.sa_graph = sa_graph
        # self.copies = copies
        self.bus_width = bus_width
        self.sa_components = _sa.SAComponents(sa_graph)
        return self.__create_sa_aws()

    def __create_sa_aws(self):
        sa_graph = self.sa_components.sa_graph
        n_cells = self.sa_components.n_cells
        n_neighbors = self.sa_components.n_neighbors
        align_bits = self.sa_components.align_bits
        n_threads = self.sa_components.n_threads

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))

        name = 'sa_aws'

        m = Module(name)

        # interface I/O interface - Begin ------------------------------------------------------------------------------
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        sa_aws_done_rd_data = m.Input('sa_aws_done_rd_data')
        sa_aws_done_wr_data = m.Input('sa_aws_done_wr_data')

        sa_aws_request_read = m.Output('sa_aws_request_read')
        sa_aws_read_data_valid = m.Input('sa_aws_read_data_valid')
        sa_aws_read_data = m.Input('sa_aws_read_data', self.bus_width)

        sa_aws_available_write = m.Input('sa_aws_available_write')
        sa_aws_request_write = m.OutputReg('sa_aws_request_write')
        sa_aws_write_data = m.OutputReg('sa_aws_write_data', self.bus_width)

        sa_aws_done = m.Output('sa_aws_done')
        # interface I/O interface - End --------------------------------------------------------------------------------

        sa_aws_done.assign(Uand(Cat(sa_aws_done_wr_data, sa_aws_done_rd_data)))

        start_pipe = m.Reg('start_pipe')

        pop_data = m.Reg('pop_data')
        available_pop = m.Wire('available_pop')
        data_out = m.Wire('data_out', self.bus_width)
        # config_valid = m.Reg('config_valid')
        config_data = m.Reg('config_data', self.bus_width)

        fsm_sd = m.Reg('fms_sd', 2)
        fsm_sd_idle = m.Localparam('fsm_sd_idle', 0, 2)
        fsm_sd_send_data = m.Localparam('fsm_sd_send_data', 1, 2)
        fsm_sd_done = m.Localparam('fsm_sd_done', 2, 2)
        flag = m.Reg('flag')

        sa_done = m.Wire('sa_done')
        sa_rd = m.Reg('sa_rd')
        sa_rd_addr = m.Reg('sa_rd_addr', t_bits + c_bits + 1)
        sa_out_v = m.Wire('sa_out_v')
        sa_out_data = m.Wire('sa_out_data', node_bits + 1)

        m.Always(Posedge(clk))(
            If(rst)(
                pop_data(0),
                fsm_sd(fsm_sd_idle),
                flag(0)
            ).Elif(start)(
                start_pipe(0),
                pop_data(0),
                flag(0),
                Case(fsm_sd)(
                    When(fsm_sd_idle)(
                        If(available_pop)(
                            pop_data(1),
                            flag(1),
                            fsm_sd(fsm_sd_send_data)
                        )
                    ),
                    When(fsm_sd_send_data)(
                        # If(available_pop | flag)(
                        config_data(data_out),
                        # pop_data(1),
                        # ).Else(
                        fsm_sd(fsm_sd_done)
                        # )
                    ),
                    When(fsm_sd_done)(
                        start_pipe(1)
                    )
                )
            )
        )

        # Data Consumer - Begin ----------------------------------------------------------------------------------------
        m.EmbeddedCode('\n//Data Consumer - Begin')
        fsm_consume = m.Reg('fsm_consume', 2)
        fsm_consume_wait = m.Localparam('fsm_consume_wait', 0)
        fsm_consume_consume = m.Localparam('fsm_consume_consume', 1)
        fsm_consume_verify = m.Localparam('fsm_consume_verify', 2)
        fsm_consume_done = m.Localparam('fsm_consume_done', 3)

        m.Always(Posedge(clk))(
            If(rst)(
                sa_rd(0),
                sa_rd_addr(0),
                sa_aws_request_write(0),
                fsm_consume(fsm_consume_wait)
            ).Else(
                sa_rd(0),
                sa_aws_request_write(0),
                Case(fsm_consume)(
                    When(fsm_consume_wait)(
                        If(sa_aws_available_write)(
                            If(sa_done)(
                                sa_rd(1),
                                fsm_consume(fsm_consume_consume),
                            ),
                        ),

                    ),
                    When(fsm_consume_consume)(
                        If(sa_out_v)(
                            sa_aws_request_write(1),
                            sa_aws_write_data(Cat(Int(0, self.bus_width - sa_out_data.width, 10), sa_out_data)),
                            sa_rd_addr.inc(),
                            fsm_consume(fsm_consume_verify)
                        ),
                    ),
                    When(fsm_consume_verify)(
                        If(sa_rd_addr == pow(2, t_bits + c_bits))(
                            fsm_consume(fsm_consume_done)
                        ).Else(
                            fsm_consume(fsm_consume_wait)
                        )
                    ),
                    When(fsm_consume_done)(

                    ),
                )
            )
        )
        m.EmbeddedCode('//Data Consumer - Begin')
        # Data Consumer - End ------------------------------------------------------------------------------------------

        fetch_data = self.sa_components.create_fecth_data(self.bus_width, self.bus_width)
        par = []
        con = [
            ('clk', clk),
            ('rst', rst),
            ('start', start),
            ('request_read', sa_aws_request_read),
            ('data_valid', sa_aws_read_data_valid),
            ('read_data', sa_aws_read_data),
            ('pop_data', pop_data),
            ('available_pop', available_pop),
            ('data_out', data_out)
        ]
        m.EmbeddedCode("(* keep_hierarchy = \"yes\" *)")
        m.Instance(fetch_data, fetch_data.name, par, con)

        par = []
        con = [
            ('clk', clk),
            ('rst', rst),
            ('start', start_pipe),
            ('n_exec', config_data),
            ('done', sa_done),
            ('rd', sa_rd),
            ('rd_addr', sa_rd_addr[:t_bits + c_bits]),
            ('out_v', sa_out_v),
            ('out_data', sa_out_data),
        ]
        aux = self.sa_components.create_sa_pipeline()
        m.Instance(aux, aux.name, par, con)

        _u.initialize_regs(m)
        return m
