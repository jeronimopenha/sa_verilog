from veriloggen import *
from math import ceil, log2
import subprocess


def to_bytes_string_list(conf_string):
    list_ret = []
    for i in range(len(conf_string), 0, -8):
        list_ret.append(conf_string[i - 8 : i])
    return list_ret


def state(val, size):
    return format(val, "0%dx" % size)


def initialize_regs(module, values=None):
    regs = []
    if values is None:
        values = {}
    flag = False
    for r in module.get_vars().items():
        if module.is_reg(r[0]):
            regs.append(r)
            if r[1].dims:
                flag = True

    if len(regs) > 0:
        if flag:
            i = module.Integer("i_initial")
        s = module.Initial()
        for r in regs:
            if values:
                if r[0] in values.keys():
                    value = values[r[0]]
                else:
                    value = 0
            else:
                value = 0
            if r[1].dims:
                genfor = For(i(0), i < r[1].dims[0], i.inc())(r[1][i](value))
                s.add(genfor)
            else:
                s.add(r[1](value))


def commands_getoutput(cmd):
    byte_out = subprocess.check_output(cmd.split())
    str_out = byte_out.decode("utf-8")
    return str_out


def bits(n):
    if n < 2:
        return 1
    else:
        return int(ceil(log2(n)))
