#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 15:00:48 2020

@author: antonio
"""
import sys
from obspy.core import UTCDateTime

#from dataclasses import dataclass

#from nordic import nordic_line1
import nordic

if len(sys.argv) < 2:
    print("Usage: read_nordic.py s-file")
    sys.exit()

nordic_file=sys.argv[1]

#nordic_file='/Users/antonio/devel/let-processing/data/test.nor'

# Nordic file can be very large, so better read line by line

in_event = False
with open(nordic_file) as fp:
    for line in fp:
        
        if len(line) != 81 and len(line.strip()) != 0:
            print('ERROR: invalid line:')
            print(line)
            sys.exit()
       
        if len(line.strip()) == 0:
            print("End of event")
            in_event = False
       
        elif line[79] == '1':
            if in_event:
                print("Ignoring extra hypocenter line for this event")
                continue
            in_event = True
            in_header = True

            hypocenter = nordic.read_line1(line)
            origin_time = UTCDateTime(hypocenter.year, hypocenter.month, hypocenter.day,
            hypocenter.hour, hypocenter.minute, hypocenter.second)
            print(origin_time)
            print(hypocenter)

        elif line[79] == 'H':
            if not in_event:
                print("High precision hypocenter line before event line")
                sys.exit()
            new_sec, new_lat, new_lon, new_depth, new_rms = nordic.read_lineH(line)
            print(new_lat)
            print(new_lon)
            print(new_depth)
           
        elif line[79] == '7':
            in_header = False

        elif line[79] == ' ' and len(line.strip()) > 5:
            pick = nordic.read_line4(line)
            print(pick)

        
        

