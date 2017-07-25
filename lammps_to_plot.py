#!/usr/bin/env python3

import argparse
import sys

from matplotlib import pyplot as plt

parser = argparse.ArgumentParser("./lammps_to_plot.py") #help='Process LAMMPS chunks file and plot'
parser.add_argument('filepath', help="Path to LAMMPS chunks output file")
parser.add_argument("--ylabel", "--yl", default="Unspecified Varname", help="variable measured in the LAMMPS file")
parser.add_argument("--xlabel", "--xl", default="chunk", help="chunk dimension")
parser.add_argument("--timesteps", "--ts", nargs=2, default=None, help="Start and stop timesteps. Defaults to plotting all.")
parser.add_argument("--timestep_size", "--tss", default=1, help="Size of timestep for proper labeling.")
parser.add_argument("--yrange", "--yr", nargs=2, default=None, help="Y Range. Defaults to total range of entire dataset.")
parser.add_argument("--xrange", "--xr", nargs=2, default=None, help="X Range. Defaults to num of chunks in LAMMPS file.")
args = parser.parse_args()

timesteps = []
values_by_timesteps = []
values = []

with open(args.filepath, 'r') as f:
    for line in f:
        if line.startswith('#'):
            pass
        elif line[0].isdigit():
            if values:
                timesteps.append(timestep)
                values_by_timesteps.append(values)
                values = []
            timestep, num_chunks, _ = line.split()

        elif line.strip() == "":
            pass
        else:
            _,_,_, temp = line.split()
            values.append(temp)

if values:
    timesteps.append(timestep)
    values_by_timesteps.append(values)

if args.timesteps:
    ts_start = int(args.timesteps[0])
    ts_stop = int(args.timesteps[1])
    ts_size = int(args.timestep_size)

    timesteps = timesteps[ts_start:ts_stop]
    values_by_timesteps = values_by_timesteps[ts_start:ts_stop]
else:
    ts_start = 0
    ts_stop = len(timesteps)
    ts_size = 1

x_range = (1, int(num_chunks))
if args.xrange:
    x_range = [float(xr) for xr in args.xrange]


if args.yrange:
    y_range = [float(yr) for yr in args.yrange]
else:
    all_values = [float(t) for values in values_by_timesteps for t in values]
    y_range = [min(all_values), max(all_values)]



alpha_min = 0.10
alpha_max = 0.50


fig = plt.figure(figsize=(8.0,6.0))
ax = fig.add_subplot(111)

ax.set_title("%s by %s [%s-%s timesteps]" % (args.ylabel, args.xlabel, ts_start * ts_size, ts_stop * ts_size))
ax.set_ylim(y_range)
ax.set_xlim(x_range)

x_range = range(1, len(values) + 1)
for i, ts in enumerate(timesteps):
    if i == len(timesteps) - 1:
        alpha = 1.00
        width = 4
    else:
        alpha = alpha_min + i*(alpha_max - alpha_min)/len(timesteps)
        width = 0.5

    ax.plot(x_range, values_by_timesteps[i], 'b', alpha=alpha, lw=width)

fig.savefig(args.filepath + ".png", dpi=144)
