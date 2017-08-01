#!/usr/bin/env python3

import argparse
import numpy as np
import re
import sys
from tabulate import tabulate

from utils import thermo_from_lammps_log

parser = argparse.ArgumentParser("./eq_trends.py")
parser.add_argument("--startdata", "-s", default=0, help="start at row. Defaults to 0.")
parser.add_argument("--nrows", "-n", default=100, help="rows to average over. Defaults to 100.")
parser.add_argument("--columns", "-c", nargs=2, action='append', metavar=('idx', 'label'), help="<column #> <label>")
parser.add_argument("--timesteps_per_row", "-t", default=10000, help="timesteps per row. Defaults to 10000.")
parser.add_argument('filepaths', nargs='+', help="Path to LAMMPS log(s)")
args = parser.parse_args()

calcs, labels = zip(*args.columns)
calcs = [int(x) for x in calcs]
startdata = int(args.startdata)
nrows = int(args.nrows)
filenames = args.filepaths
timesteps_per_row = int(args.timesteps_per_row)

cols = []
data = []
last_timestep = -1
for filename in filenames:
    print(filename)
    with open(filename, 'r') as f:
        cols1, data1 = thermo_from_lammps_log(f, last_timestep=last_timestep)
        last_timestep = data1[-1][0]
        if not cols:
            cols = cols1
        elif cols != cols1:
            print("WARNING: columns do not match: %s != %s" % (cols, cols1))

        data += data1

data = np.array(data)

def calc_stats(data, col, rowstart, rowstop, total_range, timesteps_per_row):
    x = data[:,0][rowstart:rowstop]
    y = data[:,col][rowstart:rowstop]
    a = np.vstack([x, np.ones(len(x))]).T
    slope, c = np.linalg.lstsq(a, y)[0]

    average = np.average(y)

    drange = max(y) - min(y)
    minmax = "%s to %s = %s" % (min(y), max(y), drange)

    slope_per_period = slope * (rowstop - rowstart) * timesteps_per_row
    slope_per_range_perc = slope_per_period * 100 / total_range
    slope_per_avg_perc =   slope_per_period * 100 / average

    return [minmax, average, slope, slope_per_period, "%+4.2f%%" % slope_per_range_perc, "%+4.2f%%" % slope_per_avg_perc]


def calc_row(data, calcs, rowstart, rowstop, total_range, timesteps_per_row):
    calc_row = ["%s-%s" % (rowstart, rowstop - 1)]
    for i, calc in enumerate(calcs):
        calc_row += calc_stats(data, calc, rowstart, rowstop, total_range[i], timesteps_per_row) + ['||']
    return calc_row

print()
print("Timesteps Per Row: %s" % timesteps_per_row)
print("Number rows in a period: %s" % nrows)
print("Total timesteps in a period (Ts_P): %s" % (nrows * timesteps_per_row))
print()

print("NOTE: Total Range skips the first row due to potentially high values from packing.")
total_range = [max(data[1:,calc]) - min(data[1:,calc]) for calc in calcs]

print("Total Range (TR):")
for i, calc in enumerate(calcs):
     print("- %s: %s" % (calc, total_range[i]))
print()


print("PER PERIOD")
results = []

if startdata > 0:
    rowstart = 1
    rowstop = 1 + startdata
    row = calc_row(data, calcs, rowstart, rowstop, total_range, timesteps_per_row)
    row[0] += "*"
    results.append(row)


for i in range(0,int((len(data) - startdata)/nrows)):
    rowstart = i * nrows + 1 + startdata
    rowstop = (i + 1) * nrows + 1 + startdata
    results.append(calc_row(data, calcs, rowstart, rowstop, total_range, timesteps_per_row))

headers = ["Rows"]
for i, calc in enumerate(calcs):
    headers += ["%s Range" % labels[i], "%s Average" % labels[i], "Slope (m)", "m*Ts_P", "m*Ts_P/TR", "m*Ts_P/avg", '||']

print(tabulate(results, headers, floatfmt="+.2E", stralign='right'))
print()

print("CUMULATIVE")
results = []
for i in range(0,int((len(data) - startdata)/nrows)):
    rowstart = 1 + startdata
    rowstop = (i + 1) * nrows + 1 + startdata
    row = calc_row(data, calcs, rowstart, rowstop, total_range, timesteps_per_row)
    row = [col for i,col in enumerate(row) if i==0 or ((i-1) % 7) in [1,5]]
    results.append(row)

headers = [col for i,col in enumerate(headers) if i==0 or ((i-1) % 7) in [1,5]]
print(tabulate(results, headers, floatfmt="+.2E", stralign='right'))
