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


columns = [(int(col_index) - 1, col_label) for col_index, col_label in args.columns]

if args.rows:
    row_start = int(args.rows[0])
    row_stop = int(args.rows[1])
else:
    row_start = 0
    row_stop = len(rows)


tsv = csv.reader(args.filename, delimiter="\t")
c1 = next(tsv)
c1 = next(tsv)

cols = np.ndarray(shape=(len(columns), row_stop - row_start), dtype=float)

for _ in range(0,row_start):
    next(tsv)

i = 0
for row in tsv:
    if i >= row_stop - row_start:
        print("stopping at row %i" % i)
        break
    if i >= cols.shape[1]:
        print("more rows than preallocated data structure. Please change --rows param")
        break

    for n, (col_index, col_label) in enumerate(columns):
        cols[n,i] = float(row[col_index])

    i += 1
    if i % 1000000 == 0:
        print(i)

args.filename.close()

print("std = ", np.std(cols, axis=1))
print("avg = ", np.mean(cols, axis=1))
