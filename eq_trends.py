#!/usr/bin/env python3

import numpy as np
import re
import sys
from tabulate import tabulate

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


def col_from_calc(calc):
    if re.match("\d", calc):
        return int(calc)
    else:
        return "VTPDE".index(calc) + 1


calcs = sys.argv[1] # VTPDE
startdata = int(sys.argv[2])
nrows = int(sys.argv[3])
filenames = sys.argv[4:]
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

def calc_stats(data, col, rowstart, rowstop, total_range, timesteps_per_row):
    x = data[:,0][rowstart:rowstop]
    y = data[:,col][rowstart:rowstop]
    a = np.vstack([x, np.ones(len(x))]).T
    # print(a,y)
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
        calc_row += calc_stats(data, col_from_calc(calc), rowstart, rowstop, total_range[i], timesteps_per_row) + ['||']
    return calc_row

print()
timesteps_per_row = 10000
# nrows = 200

print("Timesteps Per Row: %s" % timesteps_per_row)
print("Number rows in a period: %s" % nrows)
print("Total timesteps in a period (Ts_P): %s" % (nrows * timesteps_per_row))
print()

print("NOTE: Total Range skips the first row due to potentially high values from packing.")
total_range = [max(data[1:,col_from_calc(calc)]) - min(data[1:,col_from_calc(calc)]) for calc in calcs]

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
for calc in calcs:
    headers += ["%s Range" % calc, "%s Average" % calc, "Slope (m)", "m*Ts_P", "m*Ts_P/TR", "m*Ts_P/avg", '||']

print(tabulate(results, headers, floatfmt="+.2E", stralign='right'))
print()


results = []
for i in range(0,int((len(data) - startdata)/nrows)):
    rowstart = 1 + startdata
    rowstop = (i + 1) * nrows + 1 + startdata
    row = calc_row(data, calcs, rowstart, rowstop, total_range, timesteps_per_row)
    row = [col for i,col in enumerate(row) if i==0 or ((i-1) % 7) in [1,5]]
    results.append(row)

headers = [col for i,col in enumerate(headers) if i==0 or ((i-1) % 7) in [1,5]]
print(tabulate(results, headers, floatfmt="+.2E", stralign='right'))


# print("FROM PERIOD START TO LAST DATA POINT")
# results = []
# for i in range(0,int(len(data)/nrows)):
#     rowstart = i * nrows + 1
#     rowstop = len(data)
#     calc_row = ["%s-%s" % (rowstart, rowstop - 1)]
#     for i, calc in enumerate(calcs):
#         calc_row += calc_stats(data, col_from_calc(calc), rowstart, rowstop, total_range[i]) + ['||']
#     results.append(calc_row)
#
# print(tabulate(results, headers, floatfmt="+.2E", stralign='right'))
# print()


# for i in range(0,int(len(data)/nrows)):
#     rowstart = i * nrows
#     rowstop = len(data) - 1
#     results.append(calc_stats(data, rowstart, rowstop, total_range))
#

# print(tabulate(results, ["Rows", "Range", "Slope", "∆ (Ts_P)", "∆ / TotRange"], floatfmt="+.2E", stralign='right'))


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
