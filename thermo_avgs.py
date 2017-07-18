#!/usr/local/bin/python3

import sys

import numpy as np

filename = "J1000.out" #sys.argv[1]

def read_data(filename, delim=" "):
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#') or line.strip() == "":
                pass
            else:
                yield [float(x) for x in line.strip().split(delim)]

num_rows = 0
running_total = np.zeros(18)
for row in read_data(filename):
    num_rows += 1
    running_total += np.array(row[5:])
    running_averages = running_total / num_rows
    print(("avgs at %i: " + " %04.3f %04.3f %04.3f |"*6) % (row[0], *running_averages))
