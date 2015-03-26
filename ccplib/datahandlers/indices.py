#!/usr/bin/env python
#
# ccpdata.py
#
# Hannah Aizenman, 2012-02
# 
# http://www.opensource.org/licenses/bsd-license.php

"""This module contains routines for converting between user input and indices in 
the data. 
"""

__docformat__ = "restructuredtext"

# http://docs.python.org/2.7/library/logging.html                                  
import logging  
# http://docs.python.org/2.7/library/calendar.html
import calendar
# http://docs.python.org/2.7/library/datetime.html
import datetime
# http://docs.scipy.org/doc/numpy-1.6.0/reference/
import numpy as np
# http://pypi.python.org/pypi/coards/0.2.2
import coards

import ccplib.misc.utils

log = logging.getLogger(ccplib.misc.utils.LOGNAME)      

def coord_to_inds(lat, lon, coords, gridded = True):
    """Returns the indices for the region bounded 
    by the coordinates in coords
    :Param lat:
        Array of latitude locations of the observations in the data.
    :Param lon:
        Array of longitude locations of the observations in the data.
    :Param coords:
        Dictionary containing the region to restrict the data to:
            top: northernmost latitude
            bottom: southernmost latitude
            left: westernmost longitude
            right: easternmost longitude
        Lats and Lons can either be strings in NSEW (90N, 90S, 90E, 90W)
        convention or floats (90, -90, -90, 90) or a mix
    :Param gridded:
        Dataset is gridded LatXLon
    :return lat_lon:
        Array or list of indices of the selected region
    
    """
    
    log.debug("original coords: {!r}".format(coords))
    
    # Converts string coordinates into numbers
    top, bottom, right, left = convert_coords(lat, lon, coords)
    
    log.debug("converted coords: {!r}".format(coords))
      
    if not gridded:
        # only works if lat_1 and lon_1 are in the map
        # latitudes and longitudes are a pair
        sites = zip(lat, lon)
        lat_lon = [sites.index((la,lo)) for (la,lo) in sites
                   if top >= la >= bottom and left <= lo <= right]
        log.debug("number of site's found: {}".format(len(lat_lon)))
    else:
        # np.where = np.zero if only condition is given
        lat_inds = ((top >= lat) & (lat >= bottom)).nonzero()
        log.debug("lat shape: {}".format(lat_inds[0].shape))
        lon_inds = ((left <= lon) & (lon <= right)).nonzero()
        log.debug("lon shape: {}".format(lon_inds[0].shape))
        # builds a meshgrid from two one dimensional scalers
        lat_lon = np.ix_(lat_inds[0], lon_inds[0])
    return lat_lon

def convert_coords(lat, lon, coords):
    """ Converts string coordinates into numbers
    :Param lat:
        Array of latitude locations of the observations in the data.
    :Param lon:
        Array of longitude locations of the observations in the data.
    :Param coords:
        Dictionary containing the region to restrict the data to:
            top: northernmost latitude
            bottom: southernmost latitude
            left: westernmost longitude
            right: easternmost longitude
        Lats and Lons can either be strings in NSEW (90N, 90S, 90E, 90W)
        convention or floats (90, -90, -90, 90) or a mix
    :Returns:
        top, bottom, left, and right coordinates
    """
    for key in coords:
        if isinstance(coords[key], basestring):
            if ('S' in coords[key]) or ('W' in coords[key]):
                coords[key] = -1* float(coords[key].strip('SW'))
            elif ('N' in coords[key]) or ('E' in coords[key]):
                coords[key] = float(coords[key].strip('NE'))
            else:
                coords[key] = float(coords[key])
                
    top = coords.get('top', lat.max())
    bottom = coords.get('bottom', lat.min())
    left = coords.get('left', lon.min())
    right = coords.get('right', lon.max())
    return top, bottom, right, left

def time_to_slice(time, time_units, time_range):
    """ Returns a slice on the time axis
    :Param time: 
        array of timestamps of the observations in the data.
    :Param time_units:
        A string  of the form 'time units since reference time' 
    :Param time_range:
        Dictionary containing the time to restrict the data to:
            start: [year, *args]
            end: [year, *args]
            *args = month, day, hour, minute, second, microsecond
        Defaults to the earliest and most recent observations
        year, month, respectively used to create a python datetime object:
        http://docs.python.org/2.7/library/datetime.html
    :Return time_slice:
        Slice object from first time to last time in selected region
    
    """
    
    log.debug("time units: {}".format(time_units))

    t_start = time_range.get('start', time.min())
    log.debug("arg start time: {}".format(t_start))
    t_end = time_range.get('end', time.max())
    log.debug("arg end time: {}".format(t_end))
    
    if isinstance(t_start, list):
        datetime_start = create_start_time(t_start)
        t_start = coards.to_udunits(datetime_start, time_units) 
        log.debug("converted start time: {}".format(t_start))
        
    if isinstance(t_end, list):
        datetime_end = create_end_time(t_end)
        t_end = coards.to_udunits(datetime_end, time_units) 
        log.debug("converted end time: {}".format(t_end))
    
    # flips time if t1>t2
    if t_start>t_end:
        time2 = dict(start=time_range['end'], end=time_range['start'])
        return time_to_slice(time, time_units, time2)
    
    t_inds = ((t_start <= time) & (time <= t_end)).nonzero()[0]
    log.debug("time_inds: {}-{}".format(t_inds[0], t_inds[-1]))

    return slice(t_inds[0], t_inds[-1]+1)
    
def create_start_time(t_start):
    """Pads start time to be the first possible time
       because datetime needs year, month, day
    
    """
    
    # explicit copy so that time_range doesn't get changed
    ts_list = t_start[:]
    if len(ts_list)<3:
        ts_list.extend(['yr', 1, 1][len(ts_list):])
    return datetime.datetime(*ts_list)
                                                
def create_end_time(t_end):
    """Pads end time to be the last possible day. 
    
    """
    
    te_list = t_end[:]
    if len(te_list)==1:
        te_list.extend([12,31])
    if len(te_list)==2:
        (fday, lday) = calendar.monthrange(te_list[0], te_list[1])
        te_list.append(lday)
    return datetime.datetime(*te_list)
    
def height_to_slice(allheights, height):
    """stub for code to convert heights or pressures to indices
    """
    #will fill in once somebody requires it
    pass
