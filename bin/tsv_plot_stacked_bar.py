#!/usr/bin/env python3

import argparse
import csv
from math import ceil
import sys

from matplotlib import pyplot as plt
import numpy as np

from utils import human_format

parser = argparse.ArgumentParser("./lmp_plot_vs_time.py") #help='Process LAMMPS chunks file and plot'
parser.add_argument('filename', nargs="?", type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument("--rows", "-r", nargs=2, default=None, help="Start and stop rows. Defaults to plotting all rows.")
parser.add_argument("--avg-every", "-a", default=1, help="Number of rows to average before plotting.")
parser.add_argument("--yrange", "--yr", nargs=2, default=None, help="Y Range. Defaults to total range of entire dataset.")
parser.add_argument("--xrange", "--xr", nargs=2, default=None, help="X Range. Defaults to num of chunks in LAMMPS file.")
parser.add_argument("--columns", "-c", nargs=2, action='append', metavar=('idx', 'label'), help="<column #> <label>")
parser.add_argument("--title", default=None, help="Defaults to '<ylabel> by <xlabel>'")
parser.add_argument("--ylabel", "--yl", default="Heat Flux [Kcal / mol A^2]", help="total of all columns")
parser.add_argument("--xlabel", "--xl", default="Timestep", help="x dimension")
parser.add_argument("--timesteps-per-row", "-t", default=10000, help="timesteps per row. Defaults to 10000.")
args = parser.parse_args()


columns = [(int(col_index) - 1, col_label) for col_index, col_label in args.columns]
avg_every = int(args.avg_every)
tsv = csv.reader(args.filename, delimiter="\t")

cols = next(tsv) # skip header
data = np.array([row for row in tsv]) # , dtype=float
rows = data[:,0]
values_by_rows = np.array(data[:,1:]).astype(float)
timesteps_per_row = float(args.timesteps_per_row)

if args.rows:
    row_start = int(args.rows[0])
    row_stop = int(args.rows[1])
else:
    row_start = 0
    row_stop = len(rows)

rows=np.array(rows[row_start:row_stop], dtype=int)
values_by_rows=values_by_rows[row_start:row_stop]


if avg_every > 1:
    if len(rows) % avg_every != 0:
        print("WARNING: rows is not evenly divisible by avg-every. Truncating to largest multiple of avg-every.")
        rows = rows[0:(len(rows) // avg_every) * avg_every]
        values_by_rows=values_by_rows[0:len(rows)]
    rows = rows[avg_every-1::avg_every]
    values_by_rows=values_by_rows.reshape([len(rows), avg_every, len(values_by_rows[0,:])]).mean(1)

x_labels = [ "%s-%s" % (human_format(row - avg_every * timesteps_per_row), human_format(row)) for row in rows]

colors = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fdbf6f','#ffff99','#ff7f00','#cab2d6','#6a3d9a','#b15928','#fb9a99','#e31a1c']

num_plots = 1
bar_width = 0.65
bar_buffer = bar_width / 2
bar_indices = np.arange(len(rows))
bar_x = np.array(range(1,len(rows) + 1)) + bar_buffer


#### handle other args
if args.xrange:
    x_range = [float(xr) for xr in args.xrange]
else:
    x_range = (1, len(rows) + 1 + bar_buffer)

col_sums = np.zeros(len(rows))
for col_index, col_name in columns:
    col_sums += values_by_rows[:,col_index]

if args.yrange:
    y_range = [float(yr) for yr in args.yrange]
else:
    y_range = (0.0, col_sums.max()*1.4)

#### plot all plots
fig = plt.figure()

col_names = [c[1] for c in columns]

for plot_index in range(0, 1):
    ax = fig.add_subplot(num_plots, 1, plot_index + 1)

    if args.title:
        ax.set_title(args.title)
    else:
        ax.set_title("%s by %s" % (args.ylabel, args.xlabel))
    ax.set_xlabel(args.xlabel)
    ax.set_ylabel(args.ylabel)

    ax.grid(linestyle='-', color='0.7', zorder=0)
    ax.set_xticks(bar_x + bar_width / 2)
    ax.set_xticklabels(x_labels)
    ax.set_ylim(y_range)
    ax.set_xlim(x_range)

    prior_vals = np.zeros(len(rows))
    for col_index, col_name in columns:
        vals = values_by_rows[:,col_index]
        ax.bar(bar_x, vals, bar_width, color=colors[col_index], bottom=prior_vals, zorder=3)
        prior_vals += vals

    ax.legend(col_names)


if args.filename == sys.stdin:
    fileout = "tempout"
else:
    fileout = args.filename.name

fig.savefig(fileout + "cols.png", dpi=144)
