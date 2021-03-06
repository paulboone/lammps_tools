#!/usr/bin/env python3

import argparse
import csv
import sys

from lammps_tools.utils import thermo_from_lammps_log

parser = argparse.ArgumentParser("./lmp_log_to_tsv.py")
parser.add_argument('filenames', nargs='+', help="Path(s) to LAMMPS log output file(s)")
args = parser.parse_args()

cols = []
last_timestep = -1
tsv = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
for filename in args.filenames:
    with open(filename, 'r') as f:
        cols1, data1 = thermo_from_lammps_log(f, last_timestep=last_timestep)
        last_timestep = data1[-1][0]
        if not cols:
            cols = cols1
            tsv.writerow(cols)
        elif cols != cols1:
            raise Exception("columns of filename %s do not match prior files: %s != %s" % (filename, cols, cols1))

        tsv.writerows(data1)
