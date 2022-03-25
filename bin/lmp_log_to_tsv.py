#!/usr/bin/env python3

import argparse
import csv
import sys

import click

from lammps_tools.utils import thermo_from_lammps_log


@click.command()
@click.argument('lammps_log_path', type=click.Path())
@click.option('--thermo-index', '-i', type=int, default=1)
def lmp_log_to_tsv(lammps_log_path, thermo_index=1):
    tsv = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    with open(lammps_log_path, 'r') as f:
        cols, data = thermo_from_lammps_log(f)
        tsv.writerow(cols[thermo_index - 1])
        tsv.writerows(data[thermo_index - 1])

if __name__ == '__main__':
    lmp_log_to_tsv()
