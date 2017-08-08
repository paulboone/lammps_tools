#!/usr/bin/env python3

import argparse
import csv
import sys

parser = argparse.ArgumentParser("./lmp_chunks_to_tsv.py") #help='Process LAMMPS chunks file and plot'
parser.add_argument('filenames', nargs='+', help="Path(s) to LAMMPS chunk output file(s)")

args = parser.parse_args()

rows = []
values_by_rows = []
values = []

for filename in args.filenames:
    with open(filename, 'r') as f:
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
                _,_,_, chunkval = line.split()
                values.append(chunkval)

    if values:
        print(values_by_rows[-1])
        if len(values) != len(values_by_rows[-1]):
            raise Exception("# of chunks does not match in file %s timestep %s (%s != %s)" % (filename, timestep, len(values), len(values_by_rows[-1])))

        rows.append(timestep)
        values_by_rows.append(values)


tsv = csv.writer(sys.stdout, delimiter="\t")
tsv.writerow(['Timestep'] + list(range(1, num_chunks + 1)))
for idx, r in enumerate(rows):
    tsv.writerow([rows[idx]] + values_by_rows[idx])
