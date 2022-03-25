import re


def thermo_from_lammps_log(f, last_timestep=-1, verbose=False):
    found_data = False
    cols = []
    all_data = []
    data = []
    for line in f:
        if not found_data:
            if not line.startswith('Step'):
                pass
            else:
                cols.append(line.strip().split())
                found_data = True
        else:
            if not line.startswith("Loop"):
                data.append(line.strip().split())
            else:
                all_data.append(data)
                data = []
                found_data = False

    if len(data) > 1 and len(data[-1]) < len(data[-2]):
        if verbose:
            print("INFO: removing last row of data because it is incomplete")
        data.pop()

    return cols, all_data

def data_from_lammps_data(f, header):
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
