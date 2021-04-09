import numpy as np
import pandas as pd
import os
#from tqdm import tqdm
from tqdm.notebook import tqdm

def createColums(space_prefs, space_pos):
    for sp in space_pos:
        space_prefs[sp] = {}

def addTimeToSpacePrefs(space_prefs, time, space_pos):
    add_time = time.replace(microsecond=0)
    for sp in space_pos:
        if add_time not in space_prefs[sp]:
            space_prefs[sp][add_time] = 0

def addStayTimeToSpacePrefs(space_prefs, time, pos, stay_time):
    add_time = time.replace(microsecond=0)
    space_prefs[pos][add_time] += stay_time

def calc_pref_from_pos(file, space_pos, min_pos_dist=0):
    df = pd.read_csv(file)
    df["DateTime"] = df["DateTime"].astype('datetime64[ns]')

    space_prefs = {}
    createColums(space_prefs, space_pos)

    cur_pos = None
    cur_time = df["DateTime"][0]
    cur_time_s = cur_time.replace(microsecond=0)
    cur_p = None

    for row in tqdm(df.iterrows(), leave=True):
        p = np.array((row[1]["x_pos"], row[1]["y_pos"], row[1]["z_pos"]))
        
        if cur_p is not None:
            cur_dist = np.linalg.norm(p - cur_p)
            if cur_dist < min_pos_dist:
                continue

        cur_p = p
        min_dist = 1000
        pos = ""
        for sp in space_pos:
            d = np.linalg.norm(space_pos[sp] - p)
            if d < min_dist:
                min_dist = d
                pos = sp
        
        if cur_pos is None:
            cur_pos = pos
            cur_time = row[1]["DateTime"]
            cur_time_s = cur_time.replace(microsecond=0)
        elif cur_pos != pos:
            #time_dist_total = (row[1]["DateTime"] - cur_time).total_seconds()
            time = row[1]["DateTime"].replace(microsecond=0)
            
            while cur_time < time:
                next_time = cur_time_s + np.timedelta64(1, 's') 
                time_dist = (next_time - cur_time).total_seconds()

                addTimeToSpacePrefs(space_prefs, cur_time, space_pos)
                addStayTimeToSpacePrefs(space_prefs, cur_time, cur_pos, time_dist)

                cur_time = next_time
                cur_time_s = cur_time

            time_dist = (row[1]["DateTime"] - cur_time).total_seconds()
            addTimeToSpacePrefs(space_prefs, cur_time, space_pos)
            addStayTimeToSpacePrefs(space_prefs, cur_time, cur_pos, time_dist)
            cur_time = row[1]["DateTime"]
            cur_time_s = cur_time.replace(microsecond=0)
            cur_pos = pos

    base_name = os.path.splitext(os.path.basename(file))[0]
    parts = base_name.split('_')
    new_file_name = ""
    for p in parts[0:-1]:
        new_file_name += f"{p}_"
    new_file_name = f"{os.path.dirname(file)}{os.path.sep}{new_file_name}prefs.csv"
    
    df1 = pd.DataFrame(space_prefs)
    df1.to_csv(new_file_name)

    return new_file_name

