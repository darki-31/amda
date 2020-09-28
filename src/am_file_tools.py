import io
import os

def get_metadata(file):
    csv_file = open(file, 'rt', newline='\r\n', encoding='utf-16')

    metadata = {}

    # check header
    line = csv_file.readline()
    line = line.strip()
    if line.startswith("DateTime"):
        line = csv_file.readline()
        line = line.strip()
    
    # read ID-Device information
    while True:
        if line.startswith('#ID-Device'):
            vals = line.split(';')
            if len(vals) == 6:
                metadata[vals[1]] = {"x" : vals[2], "y" : vals[3], "z" : vals[4], "SAM" : vals[5]}
        else:
            break

        line = csv_file.readline()
        line = line.strip()
        if not line:
            break
    
    return metadata

def set_metadata(oldfile, newfile, data):
    csv_file = open(oldfile, 'rt', newline='\r\n', encoding='utf-16')
    new_file = open(newfile, 'wt', newline='\r\n', encoding='utf-16')

    # check header
    line = csv_file.readline()
    line = line.strip()
    if line.startswith("DateTime"):
        new_file.write(line + "\n")
        line = csv_file.readline()
        line = line.strip()
    
    for r in data:
        x = data[r]["x"]
        y = data[r]["y"]
        z = data[r]["z"]
        sam = data[r]["SAM"]
        new_file.write(f"#ID-Device;{r};{x};{y};{z};{sam}\n")
    
    while True:
        if not line.startswith('#'):
            new_file.write(line)
            new_file.write("\n")

        line = csv_file.readline()
        line = line.strip()
        if not line:
            break
    
    
def get_all_ids(file):
    csv_file = open(file, 'rt', newline='\r\n', encoding='utf-16')
    reader_all = []
    ids = {}

    while True:
        line = csv_file.readline()
        line = line.strip()
        if not line:
            break

        if line.startswith('#ID-Device'):
            vals = line.split(';')
            if len(vals) == 6:
                reader_all.append(vals[1])
        else:
            vals = line.split(';')
            if len(vals) > 11:
                if vals[3] in reader_all:
                    if vals[1] in ids:
                        ids[vals[1]]["events"] = ids[vals[1]]["events"] + 1
                    else:
                        ids[vals[1]] = {"name": vals[2], "events": 1}
    
    return ids


def set_names_for_ids(oldfile, newfile, ids):
    csv_file = open(oldfile, 'rt', newline='\r\n', encoding='utf-16')
    new_file = open(newfile, 'wt', newline='\r\n', encoding='utf-16')

    # check header
    line = csv_file.readline()
    line = line.strip()
    if line.startswith("DateTime"):
        new_file.write(line + "\n")
        line = csv_file.readline()
        line = line.strip()

    reader_all = []
    while True:
        if line.startswith('#ID-Device'):
            vals = line.split(';')
            if len(vals) == 6:
                new_file.write(line + "\n")
                reader_all.append(vals[1])
        else:
            vals = line.split(';')
            if len(vals) > 11:
                if vals[3] in reader_all and vals[1] in ids and ids[vals[1]] != "unknown":
                    vals[2] = ids[vals[1]]
                    add_sep = False
                    nl = ""
                    for v in vals:
                        if add_sep:
                            nl += ";"
                        nl += v
                        add_sep = True
                    new_file.write(nl + "\n")

        line = csv_file.readline()
        line = line.strip()
        if not line:
            break


def am_split(file):
    reader_am = {}
    reader_all = []
    reader_pos = {}
    am_list = []

    csv_file = open(file, 'rt', newline='\r\n', encoding='utf-16')

    # check header
    header_line = ""
    line = csv_file.readline()
    line = line.strip()
    if line.startswith("DateTime"):
        header_line = line
        line = csv_file.readline()
        line = line.strip()

    # read ID-Device information
    while True:
        if line.startswith('#ID-Device'):
            vals = line.split(';')
            if len(vals) == 6:
                if vals[5] not in am_list:
                    am_list.append(vals[5])
                
                reader_am[vals[1]] = vals[5]
                reader_all.append(vals[1])
                reader_pos[vals[1]] = [vals[2], vals[3], vals[4]]
        else:
            break

        line = csv_file.readline()
        line = line.strip()
        if not line:
            break

    if len(am_list) < 2:
        print("only one AM in file, nothing to do")
        return []

    # open one file per AM
    folder = os.path.dirname(file)
    basename = os.path.splitext(os.path.basename(file))[0]
    files = {}
    file_names = []
    for am in am_list:
        file_name = f"{folder}{os.path.sep}{am}_{basename}.csv"
        file_names.append(file_name)
        f = open(file_name, 'wt', newline='\r\n', encoding='utf-16')
        files[am] = f
        f.write(header_line + '\n')
        for r in reader_am:
            if reader_am[r] == am:
                f.write(f"#ID-Device;{r};{reader_pos[r][0]};{reader_pos[r][1]};{reader_pos[r][2]};{am}" + '\n')
    
    while True:
        vals = line.split(';')
        if len(vals) > 11:
            if vals[3] in reader_all and vals[2] != "unknown":
                am = reader_am[vals[3]]
                files[am].write(line + "\n")
        
        line = csv_file.readline()
        line = line.strip()
        if not line:
            break

    # close files
    for f in files:
        files[f].close()
    
    return file_names