# -*- coding: utf-8 -*-
"""!

@package nordic

Functions and dataclasses to read files in SEISAN's Nordic format

Currently implemented the following line types:
0 = blank card (last line of an event and file)
1 = Hypocenter line
H = 
4 = phase card
7 = phase card header

To implement:

2 = Macroseismic information
3 = Comment (or XNEAR, XFAR, SDEP for hypocenter)
5 = Error estimates (not used by SEISAN)
6 = Waveform information (file or archive)

NOTE: Type 1 line must be the first, all type 4 lines should be together and
the last line must be blank

Created on Fri Aug 21 15:00:48 2020

@author: Antonio Villasenor, ICM-CSIC
"""

from dataclasses import dataclass

@dataclass
class Hypocenter:
    year:               int = None
    month:              int = None
    day:                int = None
    fixed_time:         str = ' '
    hour:               int = None
    minute:             int = None
    second:             float = None
    location_model:     str = ' '
    distance_indicator: str = ' '
    event_type:         str = ' '
    latitude:           float = None
    longitude:          float = None
    depth:              float = None
    depth_indicator:    str = ' '
    locating_indicator: str = ' '
    locating_agency:    str = '   '
    num_sta:            int = None
    rms:                float = None
    mag1:               float = None
    mag_type1:          str = '  '
    mag_agency1:        str = '   '
    mag2:               float = None
    mag_type2:          str = '  '
    mag_agency2:        str = '   '
    mag3:               float = None
    mag_type3:          str = '  '
    mag_agency3:        str = '   '

@dataclass
class Phase_pick:
    station_name:       str = '     '
    instrument_type:    str = ' '
    component:          str = ' '
    onset:              str = ' '
    phase:              str = None
    weight_code:        int = None
    pick_mode:          str = ' '
    polarity:           str = ' '
    hour:               int = None
    minute:             int = None
    second:             float = None
    duration:           int = None
    amplitude:          float = None
    period:             float = None
    direction:          float = None
    apparent_velocity:  float = None
    incidence_angle:    float = None
    direction_residual: int = None
    residual:           float = None
    weight:             int = None
    distance:           float = None
    azimuth:            int = None

def read_line1(line):
    """! Function read_line1
    
    Reads as argument a string formatted as a Line 1 in SEISAN's Nordic format
 
    Returns a Hypocenter dataclass with all the fields in a SEISAN's Line 1

    @param[in]   line   string with SEISAN's Nordic hypocenter format (Line 1)
    @return      Hypocenter dataclass
    """

    if len(line) != 81:
        print('ERROR: invalid line length')
        
    if line[79] != '1':
        print('ERROR: invalid line type')
    
    year  = int(line[1:5])
    month = int(line[6:8])
    day   = int(line[8:10])
    
    fixed_time = line[10]   # 'F if origin time fixed'
    
    hour   = int(line[11:13])
    minute = int(line[13:15])
    if not line[16:20].isspace():
        second = float(line[16:20])
    else:
        second = None
    
    location_model     = line[20]
    distance_indicator = line[21]
    event_type         = line[22] # blank for earthquake, 'E' for explosion
    
    if not line[23:30].isspace():
        latitude = float(line[23:30])
    else:
        latitude = None

    if not line[30:38].isspace():
        longitude = float(line[30:38])
    else:
        longitude = None

    if not line[38:43].isspace():
        depth = float(line[38:43])
    else:
        depth = None
    
    depth_indicator = line[43]    # blank free depth, 'F' fixed, 'S' starting
    locating_indicator = line[44] # blank free depth, 'F' fixed, 'S' starting, '*' do not locate

    locating_agency = line[45:48]

    if not line[48:51].isspace():
        num_sta = int(line[48:51])
    else:
        num_sta = None

    if not line[51:55].isspace():
        rms = float(line[51:55])
    else:
        rms = None

    if not line[55:59].isspace():
        mag1        = float(line[55:59])
        mag_type1   = 'M' + line[59]
        mag_agency1 = line[60:63]  
    else:
        mag1        = None
        mag_type1   = ' '
        mag_agency1 = '   '
    
    if not line[63:67].isspace():
        mag2        = float(line[63:67])
        mag_type2   = 'M' + line[67]
        mag_agency2 = line[68:71]
    else:
        mag2        = None
        mag_type2   = ' '
        mag_agency2 = '   '
 
    if not line[71:75].isspace():
        mag3        = float(line[71:75])
        mag_type3   = 'M' + line[75]
        mag_agency3 = line[76:79]
    else:
        mag3        = None
        mag_type3   = ' '
        mag_agency3 = '   '        
   
    return Hypocenter(year, month, day, fixed_time, hour, minute, second,
    location_model, distance_indicator, event_type, latitude, longitude, depth, depth_indicator,
    locating_indicator, locating_agency, num_sta, rms,
    mag1, mag_type1, mag_agency1, mag2, mag_type2, mag_agency2, mag3, mag_type3, mag_agency3)

def read_lineH(line):

    if not line[16:22].isspace():
        seconds = float(line[16:22])
    else:
        seconds = None

    if not line[23:32].isspace():
        latitude = float(line[23:32])
    else:
        latitude = None

    if not line[33:43].isspace():
        longitude = float(line[33:43])
    else:
        longitude = None

    if not line[44:52].isspace():
        depth = float(line[44:52])
    else:
        depth = None

    if not line[53:59].isspace():
        rms = float(line[53:59])
    else:
        rms = None

    return seconds, latitude, longitude, depth, rms

def read_line4(line):
    """! Function read_line4
    
    @brief Reads as argument a string formatted as a Line 4 in SEISAN's Nordic format
 
    @param[in]   line   string with SEISAN's Nordic phase card format (Line 4)
    @return      Phase_pick dataclass with all the information in a phase card line

    @todo        handle error when line is shorter than 80 characters
    """
    
    station_name = line[1:6].strip()
    instrument_type = line[6]
    component = line[7]
    onset = line[9]
    phase = line[10:14].rstrip()

    if not line[14].isspace():
        weight_code = int(line[14])
    else:
        weight_code = None

    pick_mode = line[15]
    polarity = line[16]
    
    if not line[18:20].isspace():
        hour = int(line[18:20])
    else:
        hour = None
    
    if not line[20:22].isspace():
        minute = int(line[20:22])
    else:
        minute = None
        
    if not line[22:28].isspace():
        second = float(line[22:28])
    else:
        second = None
        
    if not line[29:33].isspace():
        duration = int(line[29:33])
    else:
        duration = None

    if not line[33:40].isspace():
        amplitude = float(line[33:40])
    else:
        amplitude = None

    if not line[41:45].isspace():
        period = float(line[41:45])
    else:
        period = None

    if not line[46:51].isspace():
        direction = float(line[46:51])        
    else:
        direction = None

    if not line[52:56].isspace():
        apparent_velocity = float(line[52:56])
    else:
        apparent_velocity = None
        
    if not line[56:60].isspace():
        incidence_angle = float(line[56:60])
    else:
        incidence_angle = None
        
    if not line[60:63].isspace():
        direction_residual = int(line[60:63])
    else:
        direction_residual = None

    if not line[63:68].isspace():
        residual = float(line[63:68])
    else:
        residual = None
        
    if not line[68:70].isspace():
        weight = int(line[68:70])
    else:
        weight = None

    if not line[70:75].isspace():
        distance = float(line[70:75])
    else:
        distance = None
        
    if not line[76:79].isspace():
        azimuth = int(line[76:79])
    else:
        azimuth = None
        
    return Phase_pick(station_name, instrument_type, component, onset, phase, weight_code,
    pick_mode, polarity, hour, minute, second, duration, amplitude, period,
    direction, apparent_velocity, incidence_angle, direction_residual,
    residual, weight, distance, azimuth)

