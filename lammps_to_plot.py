#!/usr/bin/env python3

import argparse
from math import ceil
import sys

from matplotlib import pyplot as plt

parser = argparse.ArgumentParser("./lammps_to_plot.py") #help='Process LAMMPS chunks file and plot'
parser.add_argument('filepath', help="Path to LAMMPS chunks output file")
parser.add_argument("--ylabel", "--yl", default="Unspecified Varname", help="variable measured in the LAMMPS file")
parser.add_argument("--xlabel", "--xl", default="chunk", help="chunk dimension")
parser.add_argument("--rows", "-r", nargs=2, default=None, help="Start and stop rows. Defaults to plotting all rows.")
parser.add_argument("--plot-every", "-p", default=None, help="Number of rows per plot.")
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

if args.rows:
    row_start = int(args.rows[0])
    row_stop = int(args.rows[1])
else:
    row_start = 0
    row_stop = len(rows)

rows=rows[row_start:row_stop]
values_by_rows=values_by_rows[row_start:row_stop]

x_range = (1, int(num_chunks))
if args.xrange:
    x_range = [float(xr) for xr in args.xrange]


if args.yrange:
    y_range = [float(yr) for yr in args.yrange]
else:
    all_values = [float(t) for values in values_by_rows for t in values]
    y_range = [min(all_values), max(all_values)]



alpha_min = 0.10
alpha_max = 0.50

if args.plot_every:
    plot_every = int(args.plot_every)
else:
    plot_every = row_stop - row_start

num_plots = ceil((row_stop - row_start) / plot_every)

fig = plt.figure(figsize=(8.0,4.0 * num_plots))
x_range = [1, len(values_by_rows[1])]

for plot_index in range(1, num_plots + 1):
    print(plot_index)
    ax = fig.add_subplot(num_plots, 1, plot_index)
    ax.set_ylim(y_range)
    ax.set_xlim(x_range)


    grow_start = plot_every * (plot_index - 1)
    grow_stop = min(plot_every * (plot_index), len(rows))

    ax.set_title("%s by %s [rows %s-%s]" % (args.ylabel, args.xlabel, grow_start + row_start, grow_stop + row_start))

    for i in range(grow_start, grow_stop):
        if i == grow_stop - 1:
            alpha = 1.00
            width = 4
        else:
            alpha = alpha_min + (i - grow_start)*(alpha_max - alpha_min)/(grow_stop - grow_start)
            width = 0.5

        ax.plot(range(x_range[0], x_range[-1] + 1), values_by_rows[i], 'b', alpha=alpha, lw=width)

fig.savefig(args.filepath + ".png", dpi=144)
