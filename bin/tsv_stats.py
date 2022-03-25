#!/usr/bin/env python3

import argparse
import csv
import re
import sys

import numpy as np
from tabulate import tabulate

from lammps_tools.utils import thermo_from_lammps_log, human_format

parser = argparse.ArgumentParser("./eq_trends.py")
parser.add_argument('filename', nargs="?", type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument("--rows", "-r", nargs=2, default=None, help="Start and stop rows. Defaults to plotting all rows.")
parser.add_argument("--columns", "-c", nargs=2, action='append', metavar=('idx', 'label'), help="<column #> <label>")
args = parser.parse_args()

columns = [int(col_index) - 1 for col_index, _ in args.columns]
column_labels = [col_label for _, col_label in args.columns]

cols = np.loadtxt(args.filename, skiprows=2, usecols=columns, dtype=float, ndmin=2)

if args.rows is not None:
    row_start = int(args.rows[0])
    row_stop = int(args.rows[1])
    cols = cols[row_start:row_stop, :]
# else:
#     row_start = 0
#     row_stop = len(rows)


std_results = np.std(cols, axis=0)
avg_results = np.mean(cols, axis=0)

print("std = ", std_results)
print("avg = ", avg_results)
print("length = ", cols.shape[1])
print("min = ", np.min(cols, axis=0))
print("max = ", np.max(cols, axis=0))

print("\t".join(["%s (avg)\t%s (std)" % (l, l) for l in column_labels]))
print("\t".join(map(str,np.dstack((avg_results, std_results)).flatten())))
