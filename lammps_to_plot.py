#!/usr/bin/env python3

import sys

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
# all_temps = [t for temps in temps_by_timesteps for t in temps]
# y_range = [min(all_temps), max(all_temps)]


from bokeh.plotting import figure, show, output_file

alpha_min = 0.25
alpha_max = 0.75

p = figure(title="Temps across Z", plot_width = 600, plot_height=400, x_range=x_range, y_range=y_range)
z_range = range(1, len(temps) + 1)
for i, ts in enumerate(timesteps):
    if i == len(timesteps) - 1:
        alpha = 1.00
        width = 2
    else:
        alpha = alpha_min + i*(alpha_max - alpha_min)/len(timesteps)
        width = 1

    p.line(z_range, temps_by_timesteps[i], line_alpha=alpha, line_width=width) # legend="y=sqrt(x)", line_color="tomato", line_dash="dotdash"

output_file(filename + ".html")
show(p)
