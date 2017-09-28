#!/usr/bin/env python3

import argparse
import csv
import sys

from utils import data_from_lammps_data

parser = argparse.ArgumentParser("./lmp_data_to_tsv.py")
parser.add_argument('filenames', nargs='+', help="Path(s) to LAMMPS log output file(s)")
parser.add_argument('--type','-t', default='atoms', help="What data to extract from data file. Can be one of [atoms, bonds, angles, dihedrals, impropers].")
args = parser.parse_args()

cols = []
last_timestep = -1
tsv = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
for filename in args.filenames:
    with open(filename, 'r') as f:
        data1 = data_from_lammps_data(f, args.type, last_timestep=last_timestep)
        tsv.writerows(data1)
