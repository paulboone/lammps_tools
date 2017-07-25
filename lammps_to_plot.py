#!/usr/bin/env python3

import sys

from matplotlib import pyplot as plt

filename = sys.argv[1]


timesteps = []
temps_by_timesteps = []
temps = []

with open(filename, 'r') as f:
    for line in f:
        if line.startswith('#'):
            pass
        elif line[0].isdigit():
            if temps:
                timesteps.append(timestep)
                temps_by_timesteps.append(temps)
                temps = []
            timestep, _, _ = line.split()

        elif line.strip() == "":
            pass
        else:
            _,_,_, temp = line.split()
            temps.append(temp)

if temps:
    timesteps.append(timestep)
    temps_by_timesteps.append(temps)
    print(temps)


timesteps = timesteps[00:100]
temps_by_timesteps = temps_by_timesteps[00:100]
y_range=(0.3,0.7)
x_range = (1,28)


alpha_min = 0.10
alpha_max = 0.50


all_temps = [float(t) for temps in temps_by_timesteps for t in temps]
y_range = [min(all_temps), max(all_temps)]
print("y_range = %s" % y_range)

fig = plt.figure(figsize=(8.0,6.0))
ax = fig.add_subplot(111)

ax.set_title("by Z")
ax.set_ylim(y_range)
ax.set_xlim(x_range)

z_range = range(1, len(temps) + 1)
for i, ts in enumerate(timesteps):
    if i == len(timesteps) - 1:
        alpha = 1.00
        width = 4
    else:
        alpha = alpha_min + i*(alpha_max - alpha_min)/len(timesteps)
        width = 0.5

    ax.plot(z_range, temps_by_timesteps[i], 'b', alpha=alpha, lw=width)

fig.savefig(filename + ".png", dpi=144)
