from veriloggen import *
from src.utils.util import initialize_regs, SaGraph
from src.hw.sa_acelerator import SaAccelerator


def create_testbench_synth(module: Module()):
    m = Module('testbench_synth')
    clk = m.Input('clk')
    rst = m.Input('rst')
    out = m.Output('out')
    regs_reset = []
    regs_inc = []
    or_list = ''

    params = module.get_params()
    for p in params:
        m.Localparam(params[p].name, params[p].value)

    ports = module.get_ports()
    con = []
    max_width_out = 1
    for port in ports:
        if module.is_input(port) and port in ['clk', 'rst']:
            con.append((port, m.get_ports()[port]))
        elif module.is_input(port) and port not in ['clk', 'rst']:
            p = ports[port]
            if p.width:
                reg = m.Reg(port, p.width)
            else:
                reg = m.Reg(port)
            regs_reset.append(reg(0))
            regs_inc.append(reg.inc())
            con.append((port, reg))
        elif module.is_output(port):
            p = ports[port]
            if p.width:
                if str(p.width) in params:
                    p.width = p.width.value

                wire = m.Wire(module.name + '_' + port, p.width)
                max_width_out = max(max_width_out, p.width)
            else:
                wire = m.Wire(module.name + '_' + port)
            or_list += wire.name + '|'
            con.append((port, wire))

    data = m.Wire('data', max_width_out)

    m.Instance(module, module.name, params, con)

    m.Always(Posedge(clk))(
        If(rst)(
            regs_reset
        ).Else(
            regs_inc
        )
    )

    data.assign(EmbeddedCode(or_list[:-1]))
    out.assign(Uxor(data))

    initialize_regs(m)

    return m


dot_file = '/home/jeronimo/Documentos/GIT/sa_verilog/dot/arf.dot'
sa_graph = SaGraph(dot_file)
sa_acc = SaAccelerator(sa_graph, 15)
m = create_testbench_synth(sa_acc.get())
m.to_verilog('synth.v')
