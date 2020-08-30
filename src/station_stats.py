#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""! Makes some basic statistics for stations in a local earthquake dataset


Created on Sat Aug 22 17:11:22 2020

@author: Antonio Villaseñor, ICM-CSIC
"""

import sys
from datetime import datetime
import math
import pandas as pd
from obspy.geodetics import gps2dist_azimuth

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import seaborn as sns

import nordic

if len(sys.argv) < 4:
    print("Usage: station_stats.py station_file nordic_file station_code")
    sys.exit()

station_file=sys.argv[1]
nordic_file=sys.argv[2]
station=sys.argv[3]

# Read station file into a Pandas dataframe

fields = ['station', 'network', 'latitude', 'longitude', 'elevation']

df = pd.read_table(station_file, delim_whitespace=True, header=None,
     usecols = [0, 1, 2, 3, 4], names=fields)

#if not df['station'].str.contains(station).any():
#    print('ERROR: string ' + station + ' not in station file')
#    sys.exit()

matches = df.index[df['station'] == station].tolist()
total_matches = len(matches)

if total_matches == 0:
    print('ERROR: station not in station file')
    sys.exit()
elif total_matches > 1:
    print('WARNING: more than one match for ' + station + ' in station file')
    sys.exit()

sta_lat = df.iloc[matches[0]]['latitude']
sta_lon = df.iloc[matches[0]]['longitude']

# Read catalog file and obtain number of P and S picks for station and earliest and latest pick

column_names = ['phase', 'pick', 'residual', 'distance', 'azimuth', 'ot', 'latitude', 'longitude', 'depth']
dfs = pd.DataFrame(columns = column_names)

num_lines = 0
line_count = 0
in_event = False
with open(nordic_file) as fp:
    for line in fp:

#       Counter to see progress reading file
        num_lines += 1
        line_count += 1
        if line_count == 100:
#           print(num_lines)
            line_count=0

        if len(line.strip()) == 0:
            in_event = False

        elif line[79] == '1':
            if in_event:
                print("Ignoring extra hypocenter line for this event")
                continue
            in_event = True
            in_header = True
            hypocenter = nordic.read_line1(line)
            if hypocenter.second > 59.999:
                hypocenter.second = 59.999
            ot_iso = '{0:4d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:09.6f}'.format( \
                     hypocenter.year, hypocenter.month, hypocenter.day, hypocenter.hour, \
                     hypocenter.minute, hypocenter.second)
            ot = datetime.fromisoformat(ot_iso)

        elif line[79] == '7':
            in_header = False

        elif line[79] == ' ' and len(line.strip()) > 5:
            if not in_event or in_header:
                print('ERROR: badly placed phase card')
                print(in_event, in_header, line)
                sys.exit()
            pick = nordic.read_line4(line)


            if pick.station_name == station:
                phase = pick.phase
                if pick.second > 59.999:
                    pick.second = 59.999
                pick_iso = '{0:4d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:09.6f}'.format( \
                     hypocenter.year, hypocenter.month, hypocenter.day, pick.hour, \
                     pick.minute, pick.second)
                pick_time = datetime.fromisoformat(pick_iso)

                phase_dict = {
                    'phase': pick.phase,
                    'pick': pick.phase,
                    'residual': pick.residual,
                    'distance': pick.distance,
                    'azimuth': pick.azimuth,
                    'ot': ot,
                    'latitude': hypocenter.latitude,
                    'longitude': hypocenter.longitude,
                    'depth': hypocenter.depth }

                dfs = dfs.append(phase_dict,ignore_index=True)

print("Number of lines read: ", num_lines)

dfp = dfs[dfs.phase == 'P']

sns.set(style='white')

g = sns.distplot(dfp[['distance']], bins=20, kde=False, rug=True)
plt.savefig('histogram.png', dpi=300)

#sns.jointplot(x = 'distance', y = 'residual', data = dfp[['distance','residual']], kind='kde')
sns.jointplot(x = 'distance', y = 'residual', data = dfp[['distance','residual']]).plot_joint(sns.kdeplot, zorder=0, n_levels=10)
plt.savefig('kde.png', dpi=300)

sns.jointplot(x = 'distance', y = 'residual', data = dfp[['distance','residual']], s=0.2)
plt.savefig('scatter.png', dpi=300)

# Plot station map

fig, ax = plt.subplots()
fig.suptitle('Station ' + station)

extent = [-17.5, -15.0, 27.5, 29.0]
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent(extent)
ax.coastlines(resolution='10m')
ax.scatter(dfp['longitude'],dfp['latitude'], marker='o', color='red', s=0.5, transform=ccrs.Geodetic())
ax.scatter(sta_lon,sta_lat, marker='^', color='green', transform=ccrs.Geodetic())

#plt.show()
plt.savefig('map.png', dpi=300)
