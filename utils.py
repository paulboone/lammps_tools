




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
                break

    if len(data[-1]) < len(data[-2]):
        print("INFO: removing last row of data because it is imcomplete")
        data.pop()

    return cols, data
