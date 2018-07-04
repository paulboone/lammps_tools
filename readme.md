## Installation

Install python3.

Installation via pip from local directory, editable:
```
git clone https://github.com/paulboone/lammps_tools.git
cd lammps_tools
pip install -e ./

# run with:
# npytraj_diffusivity.py ...

```

Running locally:
```
git clone https://github.com/paulboone/lammps_tools.git
cd lammps_tools
pip install -r requirements.txt

# run with:
# ./bin/npytraj_diffusivity.py ...

```

## Calculating diffusivity from a LAMMPS trajectory file

These assume you installed with `pip install -e` as above; if not, you'll need to call the scripts
directly.

### 1. Convert the trajectory file to a numy array:

```
lammpstrj_to_npy.py --atoms-per-molecule 3 ./gas.lammpstrj
```

The flag atoms-per-molecule is obviously 3 for CO2, but will be 2 for N2

### 2. Do block averaging and output plots and diffusivity:

```
npytraj_diffusivity.py ./lammpstrj.npy --output-molecule-plots --fs-per-row 10 --average-rows 4000
```

The --average-rows flag should be set to something that will leave you a reasonable number of
points. For a 4M row trajectory, averaging every 4000 rows, leaves you 1000 points. For a 500K row
trajectory, averaging every 500 rows will leave you with 1000 points. So this needs to be picked
appropriately for the trajectory length.
