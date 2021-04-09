import numpy as np
import pandas as pd
import math
import io
import datetime
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
#from tqdm import tqdm
from tqdm.notebook import tqdm
from calc_mean_pos import calc_mean_pos
from calc_pref_from_pos import calc_pref_from_pos
from calc_distance import calc_distance
from roaming_entropie import roaming_entropie

class ActivityMonitorDataAnalyzer:
    time_frame_ms = 500
    min_pos_dist = 0
    pos_files = []
    reader_pos = {}
    pref_files = []
    distance_files = []
    
    def __init__(self, time_frame_ms, min_pos_dist):
        self.time_frame_ms = time_frame_ms
        self.min_pos_dist = min_pos_dist
    
    def calculate(self, file):
        self.pos_files = []
        self.reader_pos = {}
        self.pref_files = []
        self.distance_files = []

        res = calc_mean_pos(file, self.time_frame_ms)
        self.reader_pos = res[1]
        self.pos_files = res[0]

        for file in tqdm(self.pos_files, desc='calculate spatial preferences', leave=True):
            pf = calc_pref_from_pos(file, self.reader_pos, self.min_pos_dist)
            self.pref_files.append(pf)
        
        for file in tqdm(self.pos_files, desc='calculate distance traveled', leave=True):
            pf = calc_distance(file, self.min_pos_dist)
            self.distance_files.append(pf)

    def scan_folder(self, folder):
        self.pos_files = []
        self.reader_pos = {}
        self.pref_files = []
        self.distance_files = []

        for file in os.listdir(folder):
            if file.endswith(".csv"):
                sp1 = file.split('_')
                try:
                    if len(sp1) == 3 and int(sp1[1]) == self.time_frame_ms:
                        sp2 = sp1[2].split('.')
                        if sp2[0] == "pos":
                            path = os.path.join(folder, file)
                            self.pos_files.append(path)
                        elif sp2[0] == "prefs":
                            path = os.path.join(folder, file)
                            self.pref_files.append(path)
                        elif sp2[0] == "dist":
                            path = os.path.join(folder, file)
                            self.distance_files.append(path)
                except ValueError:
                    pass
                

    
    def plot_roaming_entropie(self, period="1H", fig_size=(23,6)):
        files = []
        for file in self.pref_files:
            files.append((os.path.basename(file).split('_')[0], file))

        result = None
        for file in files:
            df = pd.read_csv(file[1], index_col=0, parse_dates=True)
            res = df.resample(period).sum()
            res.index.name = "DateTime"
            res[file[0]] = res.apply(lambda row: roaming_entropie(row), axis=1, raw=True)

            if result is None:
                result = res[file[0]]
            else:
                result = pd.concat([result, res[file[0]]], axis=1, join="outer")
        
        sns.set()
        sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 1.5})

        plt.figure(figsize=fig_size)
        for file in files:
            plt.plot(result.index, result[file[0]], label=file[0])

        plt.ylim(-0.01, 1)
        plt.grid(True)
        plt.margins(0.01)
        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', ncol=1)
        plt.show()

    def plot_roaming_entropie_per_day(self, period="1H", fig_size=(23,6)):
        if period != "1H" and period != "30T" and period != "15T" and period != "10T" and period != "5T":
            raise ValueError("unsupported period value.")

        files = []
        for file in self.pref_files:
            files.append((os.path.basename(file).split('_')[0], file))

        result = None
        for file in files:
            df = pd.read_csv(file[1], index_col=0, parse_dates=True)
            res = df.resample(period).sum()
            res.index.name = "DateTime"
            res[file[0]] = res.apply(lambda row: roaming_entropie(row), axis=1, raw=True)

            if result is None:
                result = res[file[0]]
            else:
                result = pd.concat([result, res[file[0]]], axis=1, join="outer")
        
        dates = result.resample("1D").sum()
        dates.index.name = "DateTime"
        dates.reset_index(inplace=True)

        x_range = []
        x_tick_pos = []
        x_tick_txt = []
        step = 60
        if period == "1H":
            step = 60
        elif period == "30T":
            step = 30
        elif period == "15T":
            step = 15
        elif period == "10T":
            step = 10
        elif period == "5T":
            step = 5
        
        pos = 0
        for h in np.arange(0, 24, 1):
            x_tick_pos.append(pos)
            x_tick_txt.append(h)
            for m in np.arange(0, 60, step):
                x_range.append(f"{h:02}:{m:02}")
                pos += 1
        
        all_ind = pd.DataFrame({"ind": x_range})
        all_ind.set_index("ind", inplace=True)

        sns.set()
        sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 1.5})

        fig, ax = plt.subplots(dates.shape[0], figsize=fig_size, sharex='all', sharey="all")

        day = 0
        for d in dates["DateTime"]:
            nd = d + np.timedelta64(23, 'h') + np.timedelta64(45, 'm')
            r = result.loc[d:nd].copy()
            r.reset_index(inplace=True)
            r["Time"] = r.apply(lambda row: row[0].strftime("%H:%M"), axis=1)
            #r["Time"] = r.apply(lambda row: row[0] - r["DateTime"][0], axis=1)
            r.set_index("Time", inplace=True)
            r2 = pd.concat([all_ind, r], axis=1, join="outer")

            for file in files:
                ax[day].plot(r2.index, r2[file[0]], label=file[0])
            
            #ax[day].title.set_text(f"day {day}")
            ax[day].title.set_text(dates["DateTime"][day].date())
            #ax[day].set_xticklabels(x_tick_txt)
            ax[day].xaxis.set_major_locator(ticker.FixedLocator(x_tick_pos))
            ax[day].xaxis.set_major_formatter(ticker.FixedFormatter(x_tick_txt))
            ax[day].set_xmargin(0.01)
            ax[day].set_ylim(-0.02, 1)
            ax[day].grid(True)

            day += 1

        plt.grid(True)
        plt.subplots_adjust(wspace=1)
        #plt.legend(ncol=2, loc='upper right')
        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', ncol=1)
        #plt.xticks(rotation=90)
        plt.show()

    def plot_distance_traveled(self, period="1H", fig_size=(23,6)):
        files = []
        for file in self.distance_files:
            files.append((os.path.basename(file).split('_')[0], file))

        result = None
        for file in files:
            df = pd.read_csv(file[1], index_col=0, parse_dates=True)
            df.rename(columns={"distance" : file[0]}, inplace=True)
            res = df.resample(period).sum()
            res.index.name = "DateTime"

            if result is None:
                result = res[file[0]]
            else:
                result = pd.concat([result, res[file[0]]], axis=1, join="outer")
        
        sns.set()
        sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 1.5})

        plt.figure(figsize=fig_size)
        for file in files:
            plt.plot(result.index, result[file[0]], label=file[0])

        plt.grid(True)
        plt.margins(0.01)
        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', ncol=1)
        plt.show()
    
    def plot_distance_traveled_per_day(self, period="1H", fig_size=(23,6)):
        if period != "1H" and period != "30T" and period != "15T" and period != "10T" and period != "5T":
            raise ValueError("unsupported period value.")

        files = []
        for file in self.distance_files:
            files.append((os.path.basename(file).split('_')[0], file))

        result = None
        for file in files:
            df = pd.read_csv(file[1], index_col=0, parse_dates=True)
            df.rename(columns={"distance" : file[0]}, inplace=True)
            res = df.resample(period).sum()
            res.index.name = "DateTime"

            if result is None:
                result = res[file[0]]
            else:
                result = pd.concat([result, res[file[0]]], axis=1, join="outer")
        
        dates = result.resample("1D").sum()
        dates.index.name = "DateTime"
        dates.reset_index(inplace=True)

        x_range = []
        x_tick_pos = []
        x_tick_txt = []
        step = 60
        if period == "1H":
            step = 60
        elif period == "30T":
            step = 30
        elif period == "15T":
            step = 15
        elif period == "10T":
            step = 10
        elif period == "5T":
            step = 5
        
        pos = 0
        for h in np.arange(0, 24, 1):
            x_tick_pos.append(pos)
            x_tick_txt.append(h)
            for m in np.arange(0, 60, step):
                x_range.append(f"{h:02}:{m:02}")
                pos += 1
        
        all_ind = pd.DataFrame({"ind": x_range})
        all_ind.set_index("ind", inplace=True)

        sns.set()
        sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 1.5})

        fig, ax = plt.subplots(dates.shape[0], figsize=fig_size, sharex='all', sharey="all")

        day = 0
        for d in dates["DateTime"]:
            nd = d + np.timedelta64(23, 'h') + np.timedelta64(45, 'm')
            r = result.loc[d:nd].copy()
            r.reset_index(inplace=True)
            r["Time"] = r.apply(lambda row: row[0].strftime("%H:%M"), axis=1)
            #r["Time"] = r.apply(lambda row: row[0] - r["DateTime"][0], axis=1)
            r.set_index("Time", inplace=True)
            r2 = pd.concat([all_ind, r], axis=1, join="outer")

            for file in files:
                ax[day].plot(r2.index, r2[file[0]], label=file[0])
            
            #ax[day].title.set_text(f"day {day}")
            ax[day].title.set_text(dates["DateTime"][day].date())
            #ax[day].set_xticklabels(x_tick_txt)
            ax[day].xaxis.set_major_locator(ticker.FixedLocator(x_tick_pos))
            ax[day].xaxis.set_major_formatter(ticker.FixedFormatter(x_tick_txt))
            ax[day].set_xmargin(0.01)
            ax[day].grid(True)

            day += 1

        plt.grid(True)
        plt.subplots_adjust(wspace=1)
        #plt.legend(ncol=2, loc='upper right')
        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', ncol=1)
        #plt.xticks(rotation=90)
        plt.show()

    def plot_accumulated_distance(self, fig_size=(23, 6)):
        files = []
        for file in self.distance_files:
            files.append((os.path.basename(file).split('_')[0], file))

        plt.figure(figsize=(24, 12))
        for file in files:
            df = pd.read_csv(file[1], index_col=0, parse_dates=True)
            df.assign(sum=df.distance.cumsum())
            df[file[0]] = df.distance.cumsum()
            plt.plot(df.index, df[file[0]], label=file[0])

        sns.set()
        sns.set_context("notebook", font_scale=1.5,
                        rc={"lines.linewidth": 1.5})

        plt.grid(True)
        plt.margins(0.01)
        plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', ncol=1)
        plt.show()
