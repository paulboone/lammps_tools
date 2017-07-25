#!/usr/bin/env python3

import argparse
from math import ceil
import sys

from matplotlib import pyplot as plt
import numpy as np

parser = argparse.ArgumentParser("./lammps_to_plot.py") #help='Process LAMMPS chunks file and plot'
parser.add_argument('filepath', help="Path to LAMMPS chunks output file")
parser.add_argument("--ylabel", "--yl", default="Unspecified Varname", help="variable measured in the LAMMPS file")
parser.add_argument("--xlabel", "--xl", default="chunk", help="chunk dimension")
parser.add_argument("--rows", "-r", nargs=2, default=None, help="Start and stop rows. Defaults to plotting all rows.")
parser.add_argument("--avg-every", "-a", default=None, help="Number of rows to average before plotting.")
parser.add_argument("--plot-every", "-p", default=None, help="Number of rows per plot. Must be a multiple of avg-every, if that is used.")
parser.add_argument("--yrange", "--yr", nargs=2, default=None, help="Y Range. Defaults to total range of entire dataset.")
parser.add_argument("--xrange", "--xr", nargs=2, default=None, help="X Range. Defaults to num of chunks in LAMMPS file.")
args = parser.parse_args()

rows = []
values_by_rows = []
values = []

with open(args.filepath, 'r') as f:
    for line in f:
        if line.startswith('#'):
            pass
        elif line[0].isdigit():
            if values:
                rows.append(timestep)
                values_by_rows.append(values)
                values = []
            timestep, num_chunks, _ = line.split()

        elif line.strip() == "":
            pass
        else:
            _,_,_, temp = line.split()
            values.append(temp)

if values:
    rows.append(timestep)
    values_by_rows.append(values)

rows = np.array(rows).astype(int)
values_by_rows = np.array(values_by_rows).astype(float)


#### handle y_range b/c if nothing passed, we want to use the full data set before it gets sliced.
if args.yrange:
    y_range = [float(yr) for yr in args.yrange]
else:
    y_range = [values_by_rows.min(), values_by_rows.max()]


#### limit rows and average, if necessary
num_chunks = int(num_chunks)
avg_every = int(args.avg_every)


if args.rows:
    row_start = int(args.rows[0])
    row_stop = int(args.rows[1])
else:
    row_start = 0
    row_stop = len(rows)

rows=rows[row_start:row_stop]
values_by_rows=values_by_rows[row_start:row_stop]

if args.avg_every:
    rows = rows[avg_every-1::avg_every]
    values_by_rows=values_by_rows.reshape([len(rows), avg_every, num_chunks]).mean(1)


#### handle other args
if args.xrange:
    x_range = [float(xr) for xr in args.xrange]
else:
    x_range = (1, int(num_chunks))

alpha_min = 0.25
alpha_max = 0.50

if args.plot_every:
    plot_every = int(args.plot_every)
else:
    plot_every = len(rows)

num_plots = ceil(len(rows) / plot_every)


#### plot all plots
fig = plt.figure(figsize=(8.0,4.0 * num_plots))
x_range = [1, num_chunks]

for plot_index in range(1, num_plots + 1):
    print(plot_index)
    ax = fig.add_subplot(num_plots, 1, plot_index)
    ax.set_ylim(y_range)
    ax.set_xlim(x_range)


    grow_start = plot_every * (plot_index - 1)
    grow_stop = min(plot_every * (plot_index), len(rows))

    text_start = row_start + grow_start * avg_every
    text_stop =  row_start + grow_stop * avg_every

    ax.set_title("%s by %s [rows %s-%s]" % (args.ylabel, args.xlabel, text_start, text_stop))

    for i in range(grow_start, grow_stop):
        if i == grow_stop - 1:
            alpha = 1.00
            width = 1
        else:
            alpha = alpha_min + (i - grow_start)*(alpha_max - alpha_min)/(grow_stop - grow_start)
            width = 0.5

        ax.plot(range(x_range[0], x_range[-1] + 1), values_by_rows[i], 'b', alpha=alpha, lw=width)

fig.savefig(args.filepath + ".png", dpi=144)
