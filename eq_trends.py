#!/usr/bin/env python3
import sys
from tabulate import tabulate
import numpy as np

def thermo_from_lammps_log(f, last_timestep=-1):
    found_data = False
    cols = []
    data = []
    for line in f:
        if not found_data:
            if not line.startswith('Step'):
                pass
            else:
                cols = line.strip().split()
                print("found columns: %s" % cols)
                found_data = True
        else:
            if not line.startswith("Loop"):
                raw_data = line.strip().split()
                raw_data[0] = int(raw_data[0])
                for i in range(1,len(raw_data)):
                    raw_data[i] = float(raw_data[i])


                if raw_data[0] == last_timestep:
                    print("INFO: skipping first line of new file b/c timestep is the same.")
                else:
                    data.append(raw_data)
            else:
                return cols, data




filenames = sys.argv[1:]
cols = []
data = []
last_timestep = -1
for filename in filenames:
    with open(filename, 'r') as f:
        cols1, data1 = thermo_from_lammps_log(f, last_timestep=last_timestep)
        last_timestep = data1[-1][0]
        if not cols:
            cols = cols1
        elif cols != cols1:
            print("WARNING: columns do not match: %s != %s" % (cols, cols1))

        data += data1


data = np.array(data)

# solve y = mx + c



def calc_stats(data, rowstart, rowstop, total_range):
    x = data[:,0][rowstart:rowstop]
    y = data[:,1][rowstart:rowstop]
    a = np.vstack([x, np.ones(len(x))]).T
    slope, c = np.linalg.lstsq(a, y)[0]

    drange = max(y) - min(y)
    minmax = "%s-%s = %s" % (min(y), max(y), drange)

    slope_per_period = slope * nrows * timesteps_per_row
    slope_range_per_mille = slope_per_period * 1000 / total_range

    return ["%s-%s" % (rowstart, rowstop), minmax, slope, slope_per_period,
                    "%+4.1f ‰" % slope_range_per_mille
                     ]

print()
timesteps_per_row = 10000
nrows = 200
total_range = max(data[:,1]) - min(data[:,1])

print("Timesteps Per Row: %s" % timesteps_per_row)
print("Number rows in a period: %s" % nrows)
print("Total timesteps in a period (Ts_P): %s" % (nrows * timesteps_per_row))
print()
print("Total Range = %s" % total_range)
print()

results = []
for i in range(0,int(len(data)/nrows)):
    rowstart = i * nrows
    rowstop = (i + 1) * nrows
    results.append(calc_stats(data, rowstart, rowstop, total_range))

print("PER PERIOD")
print(tabulate(results, ["Rows", "Range", "Slope", "∆ (Ts_P)", "(Slope / TotRange) * Ts_P"], floatfmt="+.2E", stralign='right'))
print()

results = []
for i in range(0,int(len(data)/nrows)):
    rowstart = i * nrows
    rowstop = len(data)
    results.append(calc_stats(data, rowstart, rowstop, total_range))

print("FROM PERIOD START TO LAST DATA POINT")
print(tabulate(results, ["Rows", "Range", "Slope", "∆ (Ts_P)", "(Slope / TotRange) * Ts_P"], floatfmt="+.2E", stralign='right'))


# results = []
# for i in range(0,int(len(data)/nrows)):
#     rowstart = i * nrows
#     rowstop = len(data)
#     x = data[:,0][rowstart:rowstop]
#     y = data[:,1][rowstart:rowstop]
#     a = np.vstack([x, np.ones(len(x))]).T
#     slope, c = np.linalg.lstsq(a, y)[0]
#     results.append(["%s-%s" % (rowstart, rowstop), slope])
#
# print(tabulate(results, ["Rows", "Slope"], floatfmt="+.2E"))



#

#
#
#
# # for row in data:
# #
# print(tabulate(data, cols))
