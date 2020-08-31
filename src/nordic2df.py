#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""! Converts a file in nordic format to a dataframe with all the seismic phases


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
import pyarrow.feather as feather

import nordic

if len(sys.argv) < 2:
    print("Usage: station_stats.py nordic_file")
    sys.exit()

nordic_file=sys.argv[1]

# Read catalog file and obtain number of P and S picks for station and earliest and latest pick

column_names = ['station', 'phase', 'pick', 'residual', 'distance', 'azimuth', 'ot', 'latitude', 'longitude', 'depth']
dfs = pd.DataFrame(columns = column_names)

num_lines = 0
line_count = 0
in_event = False
with open(nordic_file) as fp:
    for line in fp:

#       Counter to see progress reading file
        num_lines += 1
        line_count += 1
        if line_count == 1000:
            print(num_lines)
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

            if pick.second > 59.999:
                pick.second = 59.999
            pick_iso = '{0:4d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:09.6f}'.format( \
                 hypocenter.year, hypocenter.month, hypocenter.day, pick.hour, \
                 pick.minute, pick.second)
            pick_time = datetime.fromisoformat(pick_iso)

#           phase_dict = {
#               'station': pick.station_name,
#               'phase': pick.phase,
#               'pick': pick_time,
#               'residual': pick.residual,
#               'distance': pick.distance,
#               'azimuth': pick.azimuth,
#               'ot': ot,
#               'latitude': hypocenter.latitude,
#               'longitude': hypocenter.longitude,
#               'depth': hypocenter.depth }

            phase_df = pd.DataFrame( {
                'station': pick.station_name,
                'phase': pick.phase,
                'pick': pick_time,
                'residual': pick.residual,
                'distance': pick.distance,
                'azimuth': pick.azimuth,
                'ot': ot,
                'latitude': hypocenter.latitude,
                'longitude': hypocenter.longitude,
                'depth': hypocenter.depth } , index=[0])

#           dfs = dfs.append(phase_dict,ignore_index=True)
            dfs = pd.concat([dfs, phase_df], ignore_index=True)

print("Number of lines read: ", num_lines)

print(dfs)

feather.write_feather(dfs, 'ign.feather')
