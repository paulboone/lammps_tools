#!/usr/bin/env python3

import argparse
import sys

from matplotlib import pyplot as plt

parser = argparse.ArgumentParser("./lammps_to_plot.py") #help='Process LAMMPS chunks file and plot'
parser.add_argument('filepath', help="Path to LAMMPS chunks output file")
parser.add_argument("--ylabel", "--yl", default="Unspecified Varname", help="variable measured in the LAMMPS file")
parser.add_argument("--xlabel", "--xl", default="chunk", help="chunk dimension")
parser.add_argument("--rows", "-r", nargs=2, default=None, help="Start and stop rows. Defaults to plotting all rows.")
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
    # ts_size = int(args.timestep_size)

    rows = rows[row_start:row_stop]
    values_by_rows = values_by_rows[row_start:row_stop]
else:
    row_start = 0
    row_stop = len(rows)
    # ts_size = 1

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


fig = plt.figure(figsize=(8.0,6.0))
ax = fig.add_subplot(111)

ax.set_title("%s by %s [rows %s-%s]" % (args.ylabel, args.xlabel, row_start, row_stop))
ax.set_ylim(y_range)
ax.set_xlim(x_range)

x_range = range(1, len(values) + 1)
for i, ts in enumerate(rows):
    if i == len(rows) - 1:
        alpha = 1.00
        width = 4
    else:
        alpha = alpha_min + i*(alpha_max - alpha_min)/len(rows)
        width = 0.5

    ax.plot(x_range, values_by_rows[i], 'b', alpha=alpha, lw=width)

fig.savefig(args.filepath + ".png", dpi=144)
