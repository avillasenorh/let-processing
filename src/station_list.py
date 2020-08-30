#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""! Makes some basic statistics for stations in a local earthquake dataset


Created on Sat Aug 22 17:11:22 2020

@author: Antonio Villaseñor, ICM-CSIC
"""

import sys
import datetime
import math
import pandas as pd
from obspy.geodetics import gps2dist_azimuth
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import nordic

if len(sys.argv) < 3:
    print("Usage: station_list.py station_file nordic_file")
    sys.exit()

station_file=sys.argv[1]
nordic_file=sys.argv[2]

# Read station file into a Pandas dataframe

fields = ['station', 'network', 'latitude', 'longitude', 'elevation']

df = pd.read_table(station_file, delim_whitespace=True, header=None,
     usecols = [0, 1, 2, 3, 4], names=fields)

num_stations, nc = df.shape

# Calculate distance between all station pairs

for i in df.index:
    for j in range(i+1, num_stations):
        delta, az, baz = gps2dist_azimuth(df.loc[i, 'latitude'], df.loc[i,'longitude'],
        df.loc[j, 'latitude'], df.loc[j,'longitude'])
        
#       if (delta < 1000.0):
#           print(delta/1000.0, df.loc[i,'station'], df.loc[j,'station'])

# Read catalog file and obtain number of P and S picks for station and earliest and latest pick

dfi = df.set_index('station')

zeros = [0] * num_stations
dfi['num_p'] = zeros
dfi['num_s'] = zeros
dfi['start_date'] = zeros
dfi['end_date'] = zeros

#dum = pd.DataFrame(columns = ['station', 'num_p', 'num_s', 'start_date', 'end_date'])
#df_missing = dum.set_index('station')
cols = ['station', 'num_p', 'num_s', 'start_date', 'end_date']
df_missing = pd.DataFrame(columns = cols).set_index('station')

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

        elif line[79] == '7':
            in_header = False

        elif line[79] == ' ' and len(line.strip()) > 5:
            if not in_event or in_header:
                print('ERROR: badly placed phase card')
                print(in_event, in_header, line)
                sys.exit()
            pick = nordic.read_line4(line)
            phase = pick.phase
            phase_second = math.floor(pick.second)
            if phase_second < 0 or phase_second > 59:
                phase_second = 0
                print(line)
            phase_time = datetime.datetime(hypocenter.year, hypocenter.month, hypocenter.day,
            pick.hour, pick.minute, phase_second)

            if pick.station_name in dfi.index:

                if phase[0] == 'P':
                    dfi.loc[pick.station_name, 'num_p'] += 1
                elif phase[0] == 'S':
                    dfi.loc[pick.station_name, 'num_s'] += 1

                if dfi.loc[pick.station_name, 'start_date'] == 0 or (phase_time <
                    dfi.loc[pick.station_name, 'start_date']):
                    dfi.loc[pick.station_name, 'start_date'] = phase_time
                if dfi.loc[pick.station_name, 'end_date'] == 0 or (phase_time >
                    dfi.loc[pick.station_name, 'end_date']):
                    dfi.loc[pick.station_name, 'end_date'] = phase_time

            elif pick.station_name in df_missing.index:

                if phase[0] == 'P':
                    df_missing.loc[pick.station_name, 'num_p'] += 1
                elif phase[0] == 'S':
                    df_missing.loc[pick.station_name, 'num_s'] += 1

                if phase_time < df_missing.loc[pick.station_name, 'start_date']:
                    df_missing.loc[pick.station_name, 'start_date'] = phase_time
                if phase_time > df_missing.loc[pick.station_name, 'end_date']:
                    df_missing.loc[pick.station_name, 'end_date'] = phase_time

            else:
#               print("Missing station: " + pick.station_name)
                if phase[0] == 'P':
                    df_missing.loc[pick.station_name] = [1, 0, phase_time, phase_time]
                elif phase[0] == 'S':
                    df_missing.loc[pick.station_name] = [0, 1, phase_time, phase_time]
                

print("Number of lines read: ", num_lines)
print(dfi)

print(df_missing)

# Plot station map
extent = [-17.5, -15.0, 27.5, 29.0]

#plt.figure(figsize=(10,10))
#ax = plt.axes(projection=ccrs.PlateCarree())
#ax.set_extent(extent)
#ax.coastlines(resolution='10m')
#ax.scatter(df['longitude'],df['latitude'], marker='^', color='green', transform=ccrs.Geodetic())
#for i in df.itertuples():
#    plt.text(i.longitude, i.latitude, i.station)
#plt.show()


