#!/bin/env/python3

import sys

filename = sys.argv[1]


timestep = 0
temps = []

def output_tsv_line(timestep, temps):
    print("%s\t%s" % (timestep, "\t".join(temps)))


with open(filename, 'r') as f:
    for line in f:    
        if line.startswith('#'):
            pass
        elif line[0].isdigit():
            if temps:
                output_tsv_line(timestep, temps)

            timestep, _, _ = line.split()
            temps = []
        elif line.strip() == "":
            next
        else:
            _,_,_, temp = line.split()
            temps.append(temp)

if temps:
    output_tsv_line(timestep, temps)
