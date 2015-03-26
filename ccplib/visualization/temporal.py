#!/usr/bin/env python
#
# temporal.py
#
# Hannah Aizenman, 2011-08-12
#
# http://www.opensource.org/licenses/bsd-license.php

"""This module contains a class and methods for managing the visualization 
of temporal data.
"""

__docformat__ = "restructuredtext"


# http://docs.python.org/2.7/library/os.html#module-os
import os
# http://docs.python.org/2.7/library/logging.html
import logging

# http://docs.scipy.org/doc/numpy-1.6.0/user/
import numpy as np
# http://pypi.python.org/pypi/coards/0.2.2
import coards
# http://matplotlib.sourceforge.net/contents.html
import matplotlib
# http://matplotlib.sourceforge.net/api/dates_api.html
import matplotlib.dates
# http://matplotlib.sourceforge.net/api/ticker_api.html
import matplotlib.ticker

import ccplib
from ccplib.visualization import ccpgraph 
from ccplib.datahandlers import ccpdata, indices


log = logging.getLogger(ccplib.misc.utils.LOGNAME)

class TemporalGraph(ccpgraph.Graph):
    """Builds an object containing the attributes of a spatial graph.
    :Param CCPData:
        ccpdata object containing information about the data being
        visualized. 
    :Param kwargs:
        :Param create_folder:
            Create a folder for ouput (default is True)
        :Param save_path:
            Folder in which to save the output. 
        :Param overwrite:
            Delete existing graphs in savepath (default is False)
        :Param ext:
            File format for output (default png).        
            Any Agg supported format can be used.
        :Param center:
              Center the normalized values around a mean of 0.
              The default is 'auto' (based on a threshold)
        :Param threshold:
            Threshold for center (if center is auto)
            The default is defined in ccpgraph.Graph
        :Param title:
            The title of the graph.
        :Param xlabel:
            The label for the x axis. The default is to format
            the time stamps. 
        :Param ylabel:
            The label for the y axis.
        :Param label:
            Label the figure: The default is True.
        :Param max_ticks:
            Maximum number of ticks in the graph. 
            The default is 15
        :Param num_obs:
            Number of observations per largest unit 
            (year, month, day) There is a function that tries
            to calculate this.
            
    """
    
    def __init__(self, CCPData, **kwargs):
        """Builds the initial SpatialGraph object 
        containing the attributes of the graph.
        
        """
        ccpgraph.Graph.__init__(self, CCPData, **kwargs)
        self.__dict__.update(kwargs)
        # timeseries graphs need to be bigger
        # because of the labels
        self.figsize = (12,10)
        self.time = CCPData.time
        self.time_units = CCPData.time_units
        self.max_ticks = kwargs.get('max_ticks', 15)
        self.num_obs = kwargs.get('num_obs')

        
    def ccpshow(self, im, ax, **kwargs):
        """
        Returns an axis object containing a single temporal plot.
        :Param im:
            numpy array of the timeseries (y axis data)
        :Param ax:
            axis object for the plot
        :kwargs:
            :Param time_range:
                Dictionary of start and end points  if the time series is 
                restricted, follows the conventions for time_range: 
                    {start: start_time, end: end_time}
            :Param x data:
                Numpy array of x axis data if it isn't time.
            :Param labels:
                Dictionary containing various label fields:
                    :Param title:
                        The title of the graph.
                    :Param xlabel:
                        The label for the x axis if it isn't time.
                    :Param ylabel:
                        The label for the y axis.
                    :Param location:
                        Lat/Lon or site of the observation being plotted
                        Follows the convention of coords:
                            {top:lat1, bottom:lat2, left:lon1, right:lon2}
                    :Param alg_name:
                        Name of the algorithm applied to the data
                        
        """
        
        if hasattr(self, 'missing_value'):
            im = np.ma.masked_equal(im, self.missing_value)
        
        if self.center=='auto':
            self.center = ccpgraph.centered(im, self.threshold)
        if self.center:
            self.center_yaxis(ax, im)
        else:
            ax.set_ylim(im.min(), im.max())
        # checks if the entire array is masked
        if not im.any():
           ccpgraph.nodata(ax)
        elif 'xdata' in kwargs:
            ax.plot(kwargs['xdata'], im, linestyle = 'solid', 
                    marker = '.')
            log.debug("x/y plot")
        else:
            time_range = kwargs.get('time_range', dict())
            tsplt = ax.plot(im, linestyle = 'solid', marker = '.')
            if self.label:
                self.format_timelabels(ax, time_range)
            
        if self.label:
            labels = kwargs.get('labels', dict())
            self.set_labels(ax, **labels)
        return
    
    def format_timelabels(self, ax, time_range):
        """Formats tick marks and creates x labels
        """
        
        # pulls out times from the data
        tslice = indices.time_to_slice(self.time, self.time_units, 
                                       time_range)
        graph_times = self.time[tslice]
        
        # converts times to strings
        try:
            times = [coards.from_udunits(time, self.time_units) for time in graph_times]
        except Exception, e:
            log.exception("conversion failed: {}".format(e))
            return
        ti = ccpgraph.timestr_ind(self.time_units)
        timestr = [t.isoformat()[:ti] for t in times]
        
        if not self.num_obs:
            self.num_obs = get_num_obs(timestr, len(timestr))
        
        # place a tick and label at every base point
        base = self.get_base(len(timestr))
        dates = timestr[::base]
        
        # matplotlib formatting
        ax.xaxis.grid(True)
        ax.xaxis.set_ticks_position('bottom')
        ax.set_xlim(0, len(times))
        locater = matplotlib.ticker.MultipleLocator(base)
        ax.xaxis.set_major_locator(locater)
        ax.xaxis.set_ticklabels(dates, rotation = 45)
        log.debug("time series containing {} points".format(len(times)))
      
    def get_base(self, num_pts):
        """Tries to find a base (multiplier) that returns
        regular intervals for the ticks (e.g. every year, five months)
        based on the number of observations and the max number 
        of ticks in the graph
        :Param num_pts:
            number of timestamps in the graph
        :Return:
            Tick interval
            The default is the interval (even if it's irregular)
            that guarantees the graph will only have max_ticks amount
            of ticks.
        """
        reg_intvs = [1,5]+range(10,100,10)
        for ri in reg_intvs:
            base = self.num_obs*ri
            if (num_pts/base)<self.max_ticks:
                return base
        return (num_pts/self.max_ticks)
    
    def center_yaxis(self, ax, im):
        """Centers the yaxis at mean 0
        """
        dmax = np.ceil(np.abs(im).max())
        ax.set_ylim(-dmax, dmax)
        return
    
    def set_labels(self, ax, **kwargs):
        """
        Sets the labels based on the object, function, or labels
        """
        log.debug("Label kwargs: {!r}".format(kwargs))
        
        graph_data = [('title', 'dataset'),
                      ('ylabel', 'variable')]
                      
        labels = self.get_labels(graph_data, kwargs)
        
        if 'location' in kwargs:
            add_location_to_label(kwargs['location'], labels)
        
        ccpgraph.labelgraph(ax=ax, labels=labels)
    
def get_num_obs(dates, default):
    """Tries to automatically find the number of observations
    by calculating the difference in each field of the timestring.
    If the field is constant, then the method is called again with the
    remaining fields. 
    :Param dates:
        timestring in isoformat
    :Param default:
        Length of the original dates input. Used to keep 
        track of the default through the recursive calls.
    :Return:
        Either returns the first index where the time changes
        or default.
    """
    # This is an ugly hack that should not be relied upon
    # it's strongly recommended to just pass in the num_obs kwarg
    # Given a list [1880-10-10, 1880-10-19, 1880-11-19]:
    if len(dates) == 0:
        return default
    # cleanes the time string so that every element is seperated wth a -
    dates = [d.replace(':','-') for d in dates]
    dates = [d.replace('T','-') for d in dates]
    # breaks every element into a sublist:
        # [[1880,10,10], [1880,10,19], [1880,11,19]]
    datesegs = [d.split('-') for d in dates]
    # collects the first element of every list into a list
       # [1880, 1880, 1880]
    if isinstance(datesegs, list):
        dates = [int(dt[0]) for dt in datesegs]
    else:
        dates = [int(dt) for dt in datesegs]
    # does a diff on that list
    diffs = np.diff(dates)
    if diffs.any(): 
        # if any of the numbers differ by more than 0:
        # return the index + 1 of the first place they differ 
        return np.where(diffs)[0][0] + 1
    else:
        # assembles the spares back into lists/strings:
            #[[10-10], [10-19], [11-19]]
        rest = ['-'.join(d[1:]) for d in datesegs]
        get_num_obs(rest, default)
        
def add_location_to_label(location, labels):
    """Inserts the location into the graph
    
    """
    site = location.get('site')
    top = location.get('top')
    bottom = location.get('bottom')
    left = location.get('left')
    right = location.get('right')
    
    if site:
        locstr=site
    else:
        if (top != bottom) and bottom:
            latstr = "{} to {} Lat".format(top, bottom)
        else:
            latstr = "{} Lat".format(top)
        if (left != right) and right:
            lonstr = "{} to {} Lon".format(left, right)
        else:
            lonstr="{} Lon".format(left)
        locstr="{} and {}".format(latstr, lonstr)
    
    labels['title']= "{}\n at {}".format(labels['title'], locstr)
    return
