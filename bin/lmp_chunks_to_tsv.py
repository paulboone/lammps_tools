#!/usr/bin/env python3

import argparse
import csv
import sys

parser = argparse.ArgumentParser("./lmp_chunks_to_tsv.py") #help='Process LAMMPS chunks file and plot'
parser.add_argument('filepath', help="Path to LAMMPS chunks output file")

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
            num_chunks = int(num_chunks)
        elif line.strip() == "":
            pass
        else:
            _,_,_, temp = line.split()
            values.append(temp)

if values:
    rows.append(timestep)
    values_by_rows.append(values)

tsv = csv.writer(sys.stdout, delimiter="\t")
tsv.writerow(['Timestep'] + list(range(1, num_chunks + 1)))
for idx, r in enumerate(rows):
    tsv.writerow([rows[idx]] + values_by_rows[idx])
