#!/usr/bin/env python3

import argparse
import csv
import re
import sys

import numpy as np
from tabulate import tabulate

from lammps_tools.utils import thermo_from_lammps_log, human_format

parser = argparse.ArgumentParser("./eq_trends.py")
parser.add_argument("--startdata", "-s", default=0, help="start at row. Defaults to 0.")
parser.add_argument("--nrows", "-n", default=100, help="rows to average over. Defaults to 100.")
parser.add_argument("--columns", "-c", nargs=2, action='append', metavar=('idx', 'label'), help="<column #> <label>")
parser.add_argument('filename', nargs="?", type=argparse.FileType('r'), default=sys.stdin)
args = parser.parse_args()

calcs, labels = zip(*args.columns)
calcs = [int(x) for x in calcs]
startdata = int(args.startdata)
nrows = int(args.nrows)

tsv = csv.reader(args.filename, delimiter="\t")
cols = next(tsv)
data = np.array([row for row in tsv], dtype=float)

def calc_stats(data, col, rowstart, rowstop):
    x = data[:,0][rowstart:rowstop]
    y = data[:,col][rowstart:rowstop]
    average = np.average(y)

    drange = max(y) - min(y)
    minmax = "%s to %s = %s" % (min(y), max(y), drange)

    return [minmax, average]


def calc_row(data, calcs, rowstart, rowstop):
    calc_row = ["%i-%i" % (rowstart, rowstop)]
    calc_row += ["%s-%s" % (human_format(data[rowstart][0]), human_format(data[rowstop - 1][0]))]
    for i, calc in enumerate(calcs):
        calc_row += calc_stats(data, calc, rowstart, rowstop) + ['||']
    return calc_row

print()
print("Number rows in a period: %s" % nrows)
print()

print("PER PERIOD")
results = []

if startdata > 0:
    rowstart = 1
    rowstop = 1 + startdata
    row = calc_row(data, calcs, rowstart, rowstop)
    row[0] += "*"
    results.append(row)


for i in range(0,int((len(data) - startdata)/nrows)):
    rowstart = i * nrows + startdata
    rowstop = (i + 1) * nrows + startdata
    results.append(calc_row(data, calcs, rowstart, rowstop))

headers = ["Rows", "Timesteps"]
for i, calc in enumerate(calcs):
    headers += ["%s Range" % labels[i], "%s Average" % labels[i], '||']

print(tabulate(results, headers, floatfmt="+.2E", stralign='right'))
print()

print("CUMULATIVE")
results = []
for i in range(0,int((len(data) - startdata)/nrows)):
    rowstart = startdata
    rowstop = (i + 1) * nrows + startdata
    row = calc_row(data, calcs, rowstart, rowstop)
    row = [col for i,col in enumerate(row) if i==0 or i==1 or ((i-1) % 3) in [2]]
    results.append(row)

headers = [col for i,col in enumerate(headers) if i==0 or i==1 or ((i-1) % 3) in [2]]
print(tabulate(results, headers, floatfmt="+.2E", stralign='right'))
