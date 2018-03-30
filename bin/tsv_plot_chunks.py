#!/usr/bin/env python3

import argparse
import csv
from math import ceil
import sys

from matplotlib import pyplot as plt
from matplotlib.figure import figaspect

import numpy as np

from lammps_tools.utils import human_format

parser = argparse.ArgumentParser("./lmp_plot_chunks.py") #help='Process LAMMPS chunks file and plot'
parser.add_argument('filename', nargs="?", type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument("--output-file", "-o", default="tempout.chunks.png", help="output file name")
parser.add_argument("--ylabel", "--yl", default="Unspecified Varname", help="variable measured in the LAMMPS file")
parser.add_argument("--xlabel", "--xl", default="chunk", help="chunk dimension")
parser.add_argument("--rows", "-r", nargs=2, default=None, help="Start and stop rows. Defaults to plotting all rows.")
parser.add_argument("--avg-every", "-a", default=1, help="Number of rows to average before plotting.")
parser.add_argument("--plot-every", "-p", default=None, help="Number of rows per plot. Must be a multiple of avg-every, if that is used.")
parser.add_argument("--yrange", "--yr", nargs=2, default=None, help="Y Range. Defaults to total range of entire dataset.")
parser.add_argument("--xrange", "--xr", nargs=2, default=None, help="X Range. Defaults to num of chunks in LAMMPS file.")
parser.add_argument("--show-fit", action='store_true', help="calculate linear fit and show equation")
parser.add_argument("--vspan","-v", nargs=3, action='append', default=[], metavar=('x_start', 'x_end', 'color'), help="draw box from <x_start> to <x_end> with <color>")
parser.add_argument("--chunksize", "--cs", default=1.0, help="Chunk size")
args = parser.parse_args()

rows = []
values_by_rows = []
values = []

tsv = csv.reader(args.filename, delimiter="\t")
cols = next(tsv)
data = np.array([row for row in tsv], dtype=float)
rows = data[:,0]
values_by_rows = np.array(data[:,1:]).astype(float)
start_timesteps = rows[0]
timesteps_per_row = rows[1] - rows[0]

#### handle y_range b/c if nothing passed, we want to use the full data set before it gets sliced.
if args.yrange:
    y_range = [float(yr) for yr in args.yrange]
else:
    y_range = [values_by_rows.min(), values_by_rows.max()]


#### limit rows and average, if necessary
num_chunks = len(values_by_rows[0,:])
avg_every = int(args.avg_every)
chunksize = float(args.chunksize)

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
    values_by_rows=values_by_rows.reshape([len(rows), avg_every, num_chunks]).mean(1)


# duplicate last column so that we see a full step for the last step in step graph
num_chunks += 1
values_by_rows = np.insert(values_by_rows, -1, values_by_rows[:,-1], axis=1)

#### handle other args
if args.xrange:
    x_range = [float(xr) for xr in args.xrange]
else:
    x_range = (1, int(num_chunks))

if args.plot_every:
    plot_every = int(args.plot_every)
else:
    plot_every = len(rows)

num_plots = ceil(len(rows) / plot_every)


#### plot all plots
w, h = figaspect(0.5)
fig = plt.figure(figsize=(w,(h+1)*num_plots))
x_range = np.array([0, num_chunks-1], dtype=float) * chunksize
x_chunks = np.array(range(0, num_chunks), dtype=float) * chunksize

for plot_index in range(1, num_plots + 1):
    print("making plot # %s" % plot_index)
    ax = fig.add_subplot(num_plots, 1, plot_index)
    ax.grid(linestyle='-', color='0.7', zorder=0, which="both")
    ax.minorticks_on()
    ax.set_ylim(y_range)
    ax.set_xlim(np.array(x_range))


    grow_start = plot_every * (plot_index - 1)
    grow_stop = min(plot_every * (plot_index), len(rows))

    text_start = row_start + grow_start * avg_every
    text_stop =  row_start + grow_stop * avg_every

    ax.set_title("%s by %s: Timesteps %s-%s" % (args.ylabel, args.xlabel,
        human_format(text_start * timesteps_per_row + start_timesteps), human_format(text_stop * timesteps_per_row + start_timesteps)))
    ax.set_xlabel(args.xlabel)
    ax.set_ylabel(args.ylabel)

    plot_rows = values_by_rows[grow_start:grow_stop]

    # average rows in plot
    averaged_plot_values = plot_rows.reshape([1, grow_stop - grow_start, num_chunks]).mean(1)[0]
    ax.plot(x_chunks[0:-1] + 0.5 * chunksize, averaged_plot_values[0:-1], '#FFD700', alpha=1.0, lw=2, zorder=4)
    legend = ['overall average']

    if args.show_fit:
        # add fit line to plot
        m, c = np.linalg.lstsq(np.vstack([x_chunks[0:-1], np.ones(len(x_chunks) - 1)]).T, averaged_plot_values[0:-1])[0]
        legend += ["%.4fx + %.4f" % (m, c)]

        lin_fit_values = [m*x + c for x in x_chunks[0:-1]]
        ax.plot(x_chunks[0:-1] + 0.5 * chunksize, lin_fit_values, '#FF7F50', alpha=1.0, lw=2, zorder=5)

    for row in plot_rows:
        ax.plot(np.array(x_chunks), row, '#4682B4', alpha=0.5, lw=0.5, zorder=3, drawstyle='steps-post')

    for vs, ve, color in args.vspan:
        ax.axvspan(np.array(vs, dtype=float) * chunksize, np.array(ve, dtype=float) * chunksize, color=color)


    ax.legend(legend)

fig.savefig(args.output_file, dpi=144)
