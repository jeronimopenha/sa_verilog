import argparse
import os
import sys
import traceback
from grn2dot.grn2dot import Grn2dot

p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not p in sys.path:
    sys.path.insert(0, p)


def create_args():
    print("READING ARGS: running")
    parser = argparse.ArgumentParser('create_project -h')
    parser.add_argument('-p', '--path', help='Path to GRN databases', type=str, default='.')
    parser.add_argument('-o', '--output', help='Output folder to histogram files', type=str, default='.')
    parser.add_argument('-t', '--tname', help='Target file name', type=str, default='expressions.ALL')

    print("READING ARGS: done")
    return parser.parse_args()


def write_file(name, string):
    print("WRITE FILE: running")
    with open(name, 'w') as fp:
        fp.write(string)
        fp.close()
    print("WRITE FILE: done")


def folders_walker(path: str, tname: str) -> [str]:
    print("FOLDERS WALKER: runnning")
    content = []
    for actual_dir, dir_in_actual_dir, arch_in_actual_dir in os.walk(path):
        for a in arch_in_actual_dir:
            if str.lower(tname) in str.lower(a):
                content.append([actual_dir, a])
    print("FOLDERS WALKER: done")
    return content


def make_analysis(path: str, tname: str, output: str):
    print("MAKE HISTOGRAM: runnning")
    # look for tarhget files
    t_files = folders_walker(path, tname)
    # make the histograms
    unique_hist_dict = {}
    total_hist = {}
    for p, f in t_files:
        unique_hist_temp = {}
        grn_dot = Grn2dot("%s/%s" % (p, f))
        edges = grn_dot.get_edges_dict()
        keys = edges.keys()
        for k in keys:
            n = len(edges[k])
            if str(n) in unique_hist_temp.keys():
                unique_hist_temp[str(n)] = unique_hist_temp[str(n)] + 1
            else:
                unique_hist_temp[str(n)] = 1
            if str(n) in total_hist.keys():
                total_hist[str(n)] = total_hist[str(n)] + 1
            else:
                total_hist[str(n)] = 1
        unique_hist_dict["%s_%s" % (p.replace("/", "_"), f)] = unique_hist_temp
    to_write = {}
    for h in unique_hist_dict.keys():
        string_to_write = "neighbors, qty\n"
        for k in unique_hist_dict[h].keys():
            string_to_write = string_to_write + "%s, %s" % (k, str(unique_hist_dict[h][k])) + "\n"
        to_write[h] = string_to_write
    string_to_write = "neighbors, qty\n"
    for h in total_hist.keys():
        string_to_write = string_to_write + "%s, %s" % (h, str(total_hist[h])) + "\n"
    to_write["total_histogram"] = string_to_write

    # write files
    for f in to_write.keys():
        write_file("%s.csv"%f,to_write[f])
    print("MAKE HISTOGRAM: done")


def main():
    print("MAIN: runnning")
    args = create_args()
    running_path = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if args.output == '.':
        args.output = running_path
    if args.path == '.':
        args.path = running_path
    make_analysis(args.path, args.tname, args.output)
    print("MAIN: done")


if __name__ == '__main__':
    print("GRN NEIGHBOR ANALYSIS: running")
    try:
        main()
        print("GRN NEIGHBOR ANALYSIS: done")
    except Exception as e:
        print(e)
        traceback.print_exc()
