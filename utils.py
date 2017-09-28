import re


def thermo_from_lammps_log(f, last_timestep=-1, verbose=False):
    found_data = False
    cols = []
    data = []
    for line in f:
        if not found_data:
            if not line.startswith('Step'):
                pass
            else:
                cols = line.strip().split()
                if verbose:
                    print("found columns: %s" % cols)
                found_data = True
        else:
            if not line.startswith("Loop"):
                raw_data = line.strip().split()

                if raw_data[0] == last_timestep:
                    if verbose:
                        print("INFO: skipping first line of new file b/c timestep is the same.")
                else:
                    data.append(raw_data)
            else:
                break

    if len(data) > 1 and len(data[-1]) < len(data[-2]):
        if verbose:
            print("INFO: removing last row of data because it is imcomplete")
        data.pop()

    return cols, data

def data_from_lammps_data(f, header, last_timestep=-1, verbose=False):
    found_data = False
    data = []
    for line in f:
        if not found_data:
            if re.match(r"^ *%s"%header, line, re.IGNORECASE):
                found_data = True
        else:
            if re.match(r"^ *[a-zA-Z]", line):
                break;
            else:
                raw_data = line.strip()
                if raw_data:
                    data.append(raw_data.split())

    return data



def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '%.0f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
