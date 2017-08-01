#!/usr/bin/env python3

import argparse
import sys

from utils import thermo_from_lammps_log

parser = argparse.ArgumentParser("./lmp_log_to_tsv.py")
parser.add_argument('filepaths', nargs='+', help="Path to LAMMPS log(s)")
args = parser.parse_args()

filenames = args.filepaths

def output_tsv_line(timestep, temps):
    print("%s\t%s" % (timestep, "\t".join(temps)))


cols = []
last_timestep = -1
for filename in filenames:
    with open(filename, 'r') as f:
        cols1, data1 = thermo_from_lammps_log(f, last_timestep=last_timestep)
        last_timestep = data1[-1][0]
        if not cols:
            cols = cols1
            print("\t".join(cols))
        elif cols != cols1:
            raise Exception("columns of filename %s do not match prior files: %s != %s" % (filename, cols, cols1))

        for row in data1:
            print("\t".join(row))
#
#
#
# with open(filename, 'r') as f:
#     for line in f:
#         if line.startswith('#'):
#             pass
#         elif line[0].isdigit():
#             if temps:
#                 output_tsv_line(timestep, temps)
#
#             timestep, _, _ = line.split()
#             temps = []
#         elif line.strip() == "":
#             next
#         else:
#             _,_,_, temp = line.split()
#             temps.append(temp)
#
# if temps:
#     output_tsv_line(timestep, temps)
