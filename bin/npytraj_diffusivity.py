#!/usr/bin/env python3

import argparse
import math

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def autocorrFFT(x, N):
    N=len(x)
    F = np.fft.fft(x, n=2*N)  #2*N because of zero-padding
    PSD = F * F.conjugate()
    res = np.fft.ifft(PSD)
    res= (res[:N]).real   #now we have the autocorrelation in convention B
    n=N*np.ones(N)-np.arange(0,N) #divide res(m) by (N-m)
    return res/n #this is the autocorrelation in convention A


def msd_fft(r, N):
    N=len(r)
    D=np.square(r).sum(axis=1)
    D=np.append(D,0)
    S2=sum([autocorrFFT(r[:, i], N) for i in range(r.shape[1])])
    Q=2*D.sum()
    S1=np.zeros(N)
    for m in range(N):
        Q=Q-D[m-1]-D[N-m]
        S1[m]=Q/(N-m)
        # if m % 10000 == 0:
        #     print(m)
    return S1-2*S2

parser = argparse.ArgumentParser("./npytraj_diffusivity.py")
parser.add_argument('filename', help="Path to numpy array: should be a 3d array of row: molecule #: x, y, z")
parser.add_argument("--output-molecule-plots", action='store_true', help="output plot per molecule")
parser.add_argument("--fs-per-row", default=10, type=int, help="femtoseconds per row. Defaults to 10.")
parser.add_argument("--average-rows", default=1,  type=int, help="# of rows to average together to get a dataset of reasonable size (typically about 1000 points for graphing)")
parser.add_argument("--max-molecules", default=0,  type=int, help="maximum number of molecules to process. Useful for debugging")

# args = parser.parse_args(["./edusif/lammpstrj.npy", "--average-rows", "4000", "--output-molecule-plots", "--max-molecules", "1"])
args = parser.parse_args()

### load data and truncate to multiple of args.average_rows
data = np.load(args.filename) # row:molecule:x,y,z
num_rows, num_molecules, num_cols = data.shape
reduced_rows = num_rows // args.average_rows
num_rows = reduced_rows * args.average_rows
data = data[0:num_rows, :, :]
if args.max_molecules > 0:
    data = data[:, 0:args.max_molecules, :]
    num_molecules = args.max_molecules

# take row index for all rows, average args.average_rows number of them together, and convert to ns
simple_t = np.mean(np.arange(0,num_rows).reshape(-1, args.average_rows), axis=1) * args.fs_per_row / 1e6

### per molecule data and plots
all_results = np.zeros(reduced_rows)
simple_results = np.zeros((num_molecules, reduced_rows))
for m in range(num_molecules):
    print("Molecule %d..." % m)
    d0 = data[:,m,:][:num_rows,:] # m for mth molecule
    results = msd_fft(d0, num_rows)
    simple_results[m,:] = np.mean(results.reshape(-1, args.average_rows), axis=1)

simple_results /= 6
all_results = np.mean(simple_results, axis=0)

if args.output_molecule_plots:
    fig = plt.figure(figsize=(7,7))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlabel('tau [ns]')
    ax.set_ylabel('MSD [Ang^2]')
    ax.grid(linestyle='-', color='0.7', zorder=0)
    ax.plot(simple_t, simple_results.transpose(), zorder=2)
    fig.savefig("msd_fft_molecule_plots.png", dpi=288)

# attempt fits across different ranges
# generally for all fits, first 10% and last 50% are thrown away
# different ranges from 0.1-0.5 are tried, and fit with lowest error is selected as the
# "correct" fit and reported as the diffusivity
lin_fit_pairs = [(0.0,1.0), (0.10,0.50), (0.10,0.45), (0.10,0.40), (0.10,0.35), (0.30,0.50), (0.25,0.50), (0.20,0.50), (0.15,0.50), (0.20,0.40), (0.15,0.40), (0.20, 0.45)]
fit_results = []
highest_error = None
highest_error_pair = None
for pair in lin_fit_pairs:
    # y = at + b
    p1 = int(pair[0] * (reduced_rows - 1))
    p2 = int(pair[1] * (reduced_rows - 1))
    slope, intercept, r_value, _, _ = stats.linregress(simple_t[p1:p2], all_results[p1:p2])
    poly = (slope, intercept)
    error = r_value ** 2

    # pick best fit
    if not highest_error or error > highest_error:
        highest_error = error
        highest_error_pair = (p1,p2)
    fit_results.append([(p1,p2), error, poly])

# plot combined data and fits
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(1, 1, 1)
ax.set_xlabel('tau [ns]')
ax.set_ylabel('MSD [Ang^2]')
ax.grid(linestyle='-', color='0.7', zorder=0)
ax.plot(simple_t, all_results, zorder=10)

for r in fit_results:
    p, error, poly = r
    zorder = 2
    if p == highest_error_pair:
        print("Best fit: (%.2f - %.2f ns; r^2 = %.3f):" % (simple_t[p[0]], simple_t[p[1]], error))
        print("D = %2.2f angstrom^2 / ns" % poly[0])
        print("D = %2.3E cm^2 / s" % (poly[0] * 1e-16/1e-9))
        print("D = %2.3E m^2 / s" % (poly[0] * 1e-20/1e-9))
        zorder = 20

    ax.plot(simple_t[p[0]:p[1]], np.polyval(poly, simple_t[p[0]:p[1]]), zorder=zorder,
            label="(%.2f - %.2f ns; r^2 = %0.3f) %2.0ft + %2.0f" % (simple_t[p[0]], simple_t[p[1]], error, *poly))

ax.legend()
fig.savefig("msd_fft_all_plot.png", dpi=288)
