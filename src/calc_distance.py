import numpy as np
import pandas as pd
import os
import io
#from tqdm import tqdm
from tqdm.notebook import tqdm

def calc_distance(file, min_pos_dist=0):
    df = pd.read_csv(file)
    df["DateTime"] = df["DateTime"].astype('datetime64[ns]')

    cur_time = df["DateTime"][0]
    ev_time = cur_time
    cur_time_s = cur_time.replace(microsecond=0)
    cur_pos = np.array((df["x_pos"][0], df["y_pos"][0], df["z_pos"][0]))
    distance = 0
    distances = []

    for row in tqdm(df.iterrows()):
        ev_time = row[1]["DateTime"].replace(microsecond=0)
        p = np.array((row[1]["x_pos"], row[1]["y_pos"], row[1]["z_pos"]))

        cur_dist = np.linalg.norm(p - cur_pos)
        if cur_dist < min_pos_dist:
            continue

        if cur_time_s == ev_time:
            distance = distance + np.linalg.norm(cur_pos - p)
            cur_pos = p
        else:
            d = np.linalg.norm(cur_pos - p)
            time = row[1]["DateTime"].replace(microsecond=0)
            time_dist_total = (row[1]["DateTime"] - cur_time).total_seconds()
            dpt = d / time_dist_total

            while cur_time < time:
                next_time = cur_time_s + np.timedelta64(1, 's')
                time_dist = (next_time - cur_time).total_seconds()
                distance += time_dist * dpt

                distances.append((cur_time_s, distance))
                cur_time = next_time
                cur_time_s = cur_time
                distance = 0

            time_dist = (row[1]["DateTime"] - cur_time).total_seconds()
            distance += time_dist * dpt

            cur_time = row[1]["DateTime"]
            cur_time_s = cur_time.replace(microsecond=0)

    ev_time = ev_time.replace(microsecond=0)
    while cur_time_s < ev_time:
        distances.append((cur_time_s, 0))
        cur_time_s = cur_time_s + pd.Timedelta(seconds=1)

    base_name = os.path.splitext(os.path.basename(file))[0]
    parts = base_name.split('_')
    new_file_name = ""
    for p in parts[0:-1]:
        new_file_name += f"{p}_"
    new_file_name = f"{os.path.dirname(file)}{os.path.sep}{new_file_name}dist.csv"

    df = pd.DataFrame(distances)
    df.rename(columns={0: "DateTime", 1: "distance"}, inplace=True)
    df.set_index("DateTime", inplace=True)
    df.to_csv(new_file_name)

    return new_file_name

