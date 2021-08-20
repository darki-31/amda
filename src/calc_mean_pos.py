import numpy as np
import pandas as pd
import math
import io
import datetime
import os
#from tqdm import tqdm
from tqdm.notebook import tqdm

OLE_TIME_ZERO = datetime.datetime(1899, 12, 30, 0, 0, 0)
def ole2datetime(oledt):
    return OLE_TIME_ZERO + datetime.timedelta(days=float(oledt.replace(',','.')))

def addPoint(animal, reader, time, pos, all_data):
    if animal not in all_data:
        all_data[animal] = []
     
    all_data[animal].append({"DateTime": time, "Reader": reader, "x_pos": pos[0], "y_pos": pos[1], "z_pos": pos[2]})


def calc_mean_pos(file, timeFrameMs = 500):
    folder = os.path.dirname(file)
    reader_all = []
    reader_pos = {}
    data = {}
    timeFrame = np.timedelta64(timeFrameMs, 'ms')

    csv_file = open(file, 'rt', newline='\r\n', encoding='utf-16')
    while True:
        line = csv_file.readline()
        line = line.strip()
        if not line:
            break

        if line.startswith('#ID-Device'):
            vals = line.split(';')
            if len(vals) == 6:
                reader_all.append(vals[1])
                reader_pos[vals[1]] = np.array((int(vals[2]), int(vals[3]), int(vals[4])))
        else:
            vals = line.split(';')
            if len(vals) > 11:
                if vals[3] in reader_all and vals[2] != "unknown":
                    start_ev_time = ole2datetime(vals[0])
                    times = vals[11].split(',')
                    if len(times) > 1 and len(times) == int(vals[7]):
                        offset = 0
                        for t in times:
                            offset += int(t)
                            ev_time = start_ev_time + datetime.timedelta(milliseconds=offset)
                            addPoint(vals[2], vals[3], ev_time, reader_pos[vals[3]], data)
                    else:
                        events = int(vals[7]) - 1
                        if events > 0:
                            offset = float(vals[4]) / events
                            for e in range(events + 1):
                                ev_time = start_ev_time + datetime.timedelta(milliseconds=(e*offset))
                                addPoint(vals[2], vals[3], ev_time, reader_pos[vals[3]], data)
                        else:
                            addPoint(vals[2], vals[3], start_ev_time, reader_pos[vals[3]], data)

    csv_file.close()

    pos_file_names = []
    for animal in tqdm(data, desc='calculate mean positions', leave=True):
        pos_dic = []

        df = pd.DataFrame(data[animal])
        df["x_pos"] = df["x_pos"].astype('int64')
        df["y_pos"] = df["y_pos"].astype('int64')
        df["z_pos"] = df["z_pos"].astype('int64')
        df.sort_values(by="DateTime", inplace=True)

        positions = []        
        for row in tqdm(df.iterrows()):
            minTime = row[1]["DateTime"] - timeFrame

            if len(positions) > 0 and positions[0][0] < minTime:
                x_pos = 0.0
                y_pos = 0.0
                z_pos = 0.0
                for pos in positions:
                    x_pos += pos[1]
                    y_pos += pos[2]
                    z_pos += pos[3]
                x_pos /= len(positions)
                y_pos /= len(positions)
                z_pos /= len(positions)
                pos_dic.append((positions[0][0], x_pos, y_pos, z_pos, len(positions)))
                #print(f"{positions[0][0]} {x_pos} {y_pos} {z_pos} {len(positions)}")

            to_remove = 0
            for pos in positions:
                if pos[0] < minTime:
                    to_remove += 1
            del positions[0:to_remove]

            positions.append((row[1]["DateTime"], row[1]["x_pos"], row[1]["y_pos"], row[1]["z_pos"]))

        df = pd.DataFrame(pos_dic)
        df.rename(columns={0 : "DateTime", 1 : "x_pos", 2 : "y_pos", 3 : "z_pos", 4 : "events"}, inplace=True)
        #df["DateTime"] = df["DateTime"].astype('datetime64[ns]')
        file_name = f"{folder}{os.path.sep}{animal}_{timeFrameMs}_pos.csv"
        df.to_csv(file_name)
        pos_file_names.append(file_name)

    return (pos_file_names, reader_pos)
