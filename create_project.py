import os
import sys

if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import argparse
import traceback
from veriloggen import *
from math import ceil

from src.hw.create_axy_interface import AccAXIInterface
import src.hw.sa_acelerator as _sa
import src.utils.util as _u


# p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# if not p in sys.path:
#    sys.path.insert(0, p)


def write_file(name, string):
    with open(name, 'w') as fp:
        fp.write(string)
        fp.close()


def create_args():
    parser = argparse.ArgumentParser('create_project -h')
    parser.add_argument('-c', '--copies', help='Number of SA copies', type=int, default=1)
    parser.add_argument('-n', '--name', help='Project name', type=str, default='a.prj')
    parser.add_argument('-o', '--output', help='Project location', type=str, default='.')
    parser.add_argument('-d', '--dot', help='DOT dataflow description file', type=str)

    return parser.parse_args()


def create_project(sa_root, dot_file, copies, name, output_path):
    sa_graph = _u.SaGraph(dot_file)
    # sa_graph.n_cells = 144
    # sa_graph.n_cells_sqrt = 12
    sa_acc = _sa.SaAccelerator(sa_graph, copies)
    acc_axi = AccAXIInterface(sa_acc)

    template_path = sa_root + '/resources/template.prj'
    cmd = 'cp -r %s  %s/%s' % (template_path, output_path, name)
    _u.commands_getoutput(cmd)

    hw_path = '%s/%s/xilinx_aws_f1/hw/' % (output_path, name)
    sw_path = '%s/%s/xilinx_aws_f1/sw/' % (output_path, name)

    m = acc_axi.create_kernel_top(name)
    m.to_verilog(hw_path + 'src/%s.v' % name)

    acc_config = '#define NUM_CHANNELS (%d)\n' % sa_acc.copies
    #acc_config += '#define NUM_THREADS (%d)\n' % sa_acc.threads
    #acc_config += '#define NUM_NOS (%d)\n' % sa_acc.nodes_qty
    #acc_config += '#define STATE_SIZE_WORDS (%d)\n' % ceil(sa_acc.nodes_qty / 8)
    #acc_config += '#define BUS_WIDTH_BYTES (%d)\n' % (sa_acc.bus_width // 8)
    #acc_config += '#define OUTPUT_DATA_BYTES (%d)\n' % (ceil(bits_width / bus_width) * bus_width // 8)
    #acc_config += '#define ACC_DATA_BYTES (%d)\n' % (sa_acc.axi_bus_data_width // 8)

    num_axis_str = 'NUM_M_AXIS=%d' % sa_acc.get_num_in()
    conn_str = acc_axi.get_connectivity_config(name)

    write_file(hw_path + 'simulate/num_m_axis.mk', num_axis_str)
    write_file(hw_path + 'synthesis/num_m_axis.mk', num_axis_str)
    write_file(sw_path + 'host/prj_name', name)
    write_file(sw_path + 'host/include/acc_config.h', acc_config)
    write_file(hw_path + 'simulate/prj_name', name)
    write_file(hw_path + 'synthesis/prj_name', name)
    write_file(hw_path + 'simulate/vitis_config.txt', conn_str)
    write_file(hw_path + 'synthesis/vitis_config.txt', conn_str)


def main():
    args = create_args()
    running_path = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sa_root = os.getcwd()

    if args.output == '.':
        args.output = running_path

    if args.dot:
        #args.dot = running_path + '/' + args.dot
        create_project(sa_root, args.dot, args.copies, args.name, args.output)
        print('Project successfully created in %s/%s' % (args.output, args.name))
    else:
        msg = 'Missing parameters. Run create_project -h to see all parameters needed'
        raise Exception(msg)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)
        traceback.print_exc()
