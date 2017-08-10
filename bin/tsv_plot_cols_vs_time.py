#!/usr/bin/env python3

import argparse
import csv
from math import ceil
import sys

from matplotlib import pyplot as plt
import numpy as np

parser = argparse.ArgumentParser("./lmp_plot_vs_time.py") #help='Process LAMMPS chunks file and plot'
parser.add_argument('filename', nargs="?", type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument("--rows", "-r", nargs=2, default=None, help="Start and stop rows. Defaults to plotting all rows.")
parser.add_argument("--avg-every", "-a", default=1, help="Number of rows to average before plotting.")
parser.add_argument("--yrange", "--yr", nargs=2, default=None, help="Y Range. Defaults to total range of entire dataset.")
parser.add_argument("--xrange", "--xr", nargs=2, default=None, help="X Range. Defaults to num of chunks in LAMMPS file.")
parser.add_argument("--columns", "-c", nargs=2, action='append', metavar=('idx', 'label'), help="<column #> <label>")
args = parser.parse_args()

avg_every = int(args.avg_every)
tsv = csv.reader(args.filename, delimiter="\t")

cols = next(tsv)
data = np.array([row for row in tsv], dtype=float)
rows = data[:,0]
values_by_rows = np.array(data[:,1:]).astype(float)

if args.rows:
    row_start = int(args.rows[0])
    row_stop = int(args.rows[1])
else:
    row_start = 0
    row_stop = len(rows)

rows=rows[row_start:row_stop]
values_by_rows=values_by_rows[row_start:row_stop]


if avg_every > 1:
    if len(rows) % avg_every != 0:
        print("WARNING: rows is not evenly divisible by avg-every. Truncating to largest multiple of avg-every.")
        rows = rows[0:(len(rows) // avg_every) * avg_every]
        values_by_rows=values_by_rows[0:len(rows)]
    rows = rows[avg_every-1::avg_every]
    values_by_rows=values_by_rows.reshape([len(rows), avg_every, len(values_by_rows[0,:])]).mean(1)

#### handle other args
if args.xrange:
    x_range = [float(xr) for xr in args.xrange]
else:
    x_range = (min(rows), max(rows))


num_plots = ceil(len(args.columns))


#### plot all plots
fig = plt.figure(figsize=(8.0,4.0 * num_plots))

for plot_index in range(0, num_plots):
    col = int(args.columns[plot_index][0])
    ax = fig.add_subplot(num_plots, 1, plot_index + 1)
    ax.set_title("%s by timestep" % (args.columns[plot_index][1]))
    ax.grid(linestyle='-', color='0.7', zorder=0)

    values = values_by_rows[:, col]

    if args.yrange:
        y_range = [float(yr) for yr in args.yrange]
    else:
        y_range = [values.min(), values.max()]

    ax.set_ylim(y_range)
    ax.set_xlim(x_range)

    ax.plot(rows, values, 'b', zorder=3)

if args.filename == sys.stdin:
    fileout = "tempout"
else:
    fileout = args.filename.name

fig.savefig(fileout + ".png", dpi=144)
