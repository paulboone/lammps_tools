#!/usr/bin/env python3

import argparse
import csv
import sys

from lammps_tools.utils import data_from_lammps_data

parser = argparse.ArgumentParser("./lmp_data_to_tsv.py")
parser.add_argument('filenames', nargs='+', help="Path(s) to LAMMPS log output file(s)")
args = parser.parse_args()

data = []
for filename in args.filenames:
    with open(filename, 'r') as f:
        data += data_from_lammps_data(f, "atoms")

fh = sys.stdout
fh.write("%d\n" % len(data))
fh.write("source: lammps data from %s\n" % args.filenames)
for row in data:
    _, _, atom_type, _, x, y, z = row
    atom_type = atom_type.rjust(3)
    x = float(x); y = float(y); z = float(z)
    fh.write("%s%10.5f%10.5f%10.5f\n" % (atom_type, x, y, z))
