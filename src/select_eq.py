#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 13:36:27 2020

@author: antonio
"""
from obspy.io.nordic.core import read_nordic # , readheader

nordic_file='/Users/antonio/devel/let-processing/data/test.nor'

#catalog = readheader(nordic_file)

catalog = read_nordic(nordic_file, return_wavnames=False)
#print(type(catalog))
#print(dir(catalog))

#print(catalog)
#print(catalog.__str__(print_all=True))

test_event = catalog.events[0]
print(type(test_event))
print(dir(test_event))

#print(test_event.magnitudes)
#print(type(test_event.magnitudes))

print(test_event)
print(test_event.event_type)
print(test_event.picks)