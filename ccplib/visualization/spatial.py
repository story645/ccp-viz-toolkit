#!/usr/bin/env python
#
# spatial.py
#
# Hannah Aizenman, 2011-07
#
# http://www.opensource.org/licenses/bsd-license.php

"""This module contains a class for managing the visualization of spatial
data and associated methods.
"""

__docformat__ = "restructuredtext"

# http://docs.python.org/2.7/library/os.html#module-os
import os
# http://docs.python.org/2.7/library/logging.html
import logging
# http://docs.python.org/2.7/library/datetime.html
import datetime

# http://pypi.python.org/pypi/coards/0.2.2
import coards
# http://docs.scipy.org/doc/numpy-1.6.0/user/
import numpy as np
# http://matplotlib.sourceforge.net/contents.html
import matplotlib
# http://matplotlib.sourceforge.net/api/cm_api.html
import matplotlib.cm 
# http://matplotlib.sourceforge.net/api/axes_api.html 
import matplotlib.axes
# http://matplotlib.sourceforge.net/api/ticker_api.html
import matplotlib.ticker
# http://matplotlib.sourceforge.net/basemap/doc/html/api/basemap_api.html
from mpl_toolkits.basemap import Basemap
# http://matplotlib.sourceforge.net/mpl_toolkits/axes_grid/index.html
import mpl_toolkits.axes_grid

import ccplib
from ccplib.datahandlers import ccpdata, indices
from ccplib.visualization import ccpgraph

log = logging.getLogger(ccplib.misc.utils.LOGNAME)

class SpatialGraph(ccpgraph.Graph):
    """Builds an object containing the attributes of a spatial graph.
    :Param CCPData:
        CCPData object containing information about the data being
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
        :Param title:
            The title of the graph.
        :Param xlabel:
            The label for the x axis. 
        :Param ylabel:
            The label for the y axis.
        :Param cblabel:
            The label for the colorbar.
        :Param projection:
            Map the data should be projected in.
        :Param alt_projection:
            Projection to be used if the data is restricted
        :Param map_grid:
            Draw parallels and meridians: default is True.
            :Param par_deg:
                The degree between lat lines. The default is 30.
            :Param mer_deg:
                The degree between lon lines. The default is 60.
        :Param cmap:
            The colormap used to visualize the data. The default is 'jet',
            and a list can be found at:
            http://matplotlib.sourceforge.net/examples/pylab_examples/show_colormaps.html
        :Param center_cmap:
            Colormap to use if the data is centered. The default is cmap.
        :Param colorbar:
            Add a colorbar to the graph. The default is True
        :Param colorbar_orientation:
            The options are 'vertical' or 'horizontal'.
            The default is 'horizontal'. 
        :Param center:
            Center the normalized values around a mean of 0. 
            The default is 'auto' (based on a threshold)
        :Param discrete:
            Bin the values for the visualization
        :Param threshold:
            Threshold for center (if center is auto)
            The default is defined in ccpgraph.Graph
        :Param center_cmap:
            Use a different cmap if centered
        :Param label:
            Label the figure: The default is True. 
    """
    
    def __init__(self, CCPData, **kwargs):
        """Builds the initial SpatialGraph object 
        containing the attributes of the graph.

        """
        # explicitely inherit attributes from ccpgraph 
        ccpgraph.Graph.__init__(self, CCPData, **kwargs)
        self.__dict__.update(kwargs)
        self.figsize = None
            
        # Map related attributes
        self.lat = CCPData.lat
        self.lon = CCPData.lon
        self.map_grid = kwargs.get('map_grid', True)
        if self.map_grid:
            self.par_deg = kwargs.get('par_deg', 30.0)
            self.mer_deg = kwargs.get('mer_deg', 60.0)
        #Coloring attributes
        cmap_name = kwargs.get('cmap', 'jet')
        self.discrete = kwargs.get('discrete')
        if isinstance(cmap_name, basestring):
            self.cmap = matplotlib.cm.get_cmap(name=cmap_name)
        else:
            self.cmap = cmap_name
        self.colorbar =  kwargs.get('colorbar', True)
        
        if self.colorbar:
            self.orientation = kwargs.get('colorbar_orientation',
                                          'horizontal')
        
        if hasattr(self, 'data_labels') and (CCPData, 'time_units'):
            self.data_labels.update(time_units=CCPData.time_units)
            
        if hasattr(CCPData, 'time'):
            self.dtime = (CCPData.time.min(), CCPData.time.max())
            self.time_units = CCPData.time_units
        else:
            self.dtime = None
            self.time_units = None
        
    def ccpshow(self, im, ax, **kwargs):
        """
        Returns an axis object containing a single spatial plot.
        :Param im:
            Numpy array of the image
        :Param ax:
            Axis for the plot
        kwargs:
            :Param coords:
                Dictionary of bounding coordinates of the map 
                if the map is restricted.
                Follows the convention of coords:
                     {top:lat1, bottom:lat2, left:lon1, right:lon2}
            :Param bounds:
                Boundaries to use for a collection of variables.
                Used for batch graphs
                Of the form (min, max)
            :Param labels:
                Dictionary containing various label fields:
                    :Param title:
                        The title of the graph.
                    :Param xlabel:
                        The label for the x axis.
                    :Param ylabel:
                        The label for the y axis.
                    :Param cblabel:
                        The label for the colorbar.
                    :Param time:
                        Dictionary of start and end points  if the time series is
                        restricted, follows the conventions for time_range:
                            {start: start_time, end: end_time}
                    :Param freq:
                        unidate time_unit string or frequency of observations
                        (i.e. years, months, etc)
                    :Param alg_name:
                        Name of the algorithm applied to the data
                
        """
        if hasattr(self, 'missing_value'):
            # Converts an array with missing values to a masked array.
            im = np.ma.masked_equal(im, self.missing_value)
           
        if self.center == "auto":
            self.center = ccpgraph.centered(im, self.threshold)

        if (self.center and hasattr(self, 'center_cmap')):
            if isinstance(self.center_cmap, basestring):
                self.cmap = matplotlib.cm.get_cmap(name=self.center_cmap)
            else:
                self.cmap = self.center_cmap
                
        bounds = kwargs.get('bounds')
        self.discrete = kwargs.get('discrete', self.discrete)
        self.norm = self.get_norm(im, bounds)
        
        #add some stuff here about gridded and non-gridded    
        if hasattr(self,'projection'):
            coords = kwargs.get('coords', dict())
            self.mapped_plot(im, ax, coords = coords)
        else:
            # Plots the data without a map if no projection is defined
            ax.matshow(im, cmap=self.cmap, norm=self.norm, 
                           aspect='equal', interpolation='nearest')
        if self.colorbar:
            cb = self.get_colorbar(ax, im)
        else:
            cb = None
        
        if self.label:
            labels = kwargs.get('labels', dict())
            self.set_labels(ax, cb, **labels)
        return 
    
    def get_projection_params(self, coords=dict()):
        """Calculates the parameters for the projections.
        
        """
        
        (lat_i, lon_j) = indices.coord_to_inds(self.lat, self.lon, coords)
        # squeeze is used to keep the arrays 1d
        lat = self.lat[lat_i].squeeze()
        lon = self.lon[lon_j].squeeze()
        
        # Still need to figure out how lat_1/2, and lon_1/2 work.
        proj_params = dict( llcrnrlat=lat[-1], 
                            urcrnrlat=lat[0],
                            llcrnrlon=lon[0], 
                            urcrnrlon=lon[-1], 
                            lat_0=np.median(lat[:]),  
                            lon_0=np.median(lon[:])
                            )
                            
        log.debug("projection parameters: {!r}".format(proj_params))
        return (proj_params, lat, lon)
        
    def mapped_plot(self, im, ax, coords=None):
        """Returns an image of the projected data. 
        """
        (proj_kwargs, lat, lon) = self.get_projection_params(coords)
        
        # Tries to figure out if the data is restricted
        lat_subset = (len(lat)<len(self.lat))
        lon_subset = (len(lon)<len(self.lon))
        proj_flag = (lat_subset or lon_subset)
                    
        # Some projections look terrible on restricted graphs
        # so the user can provide a backup:
        if (hasattr(self, 'alt_projection') and proj_flag):
            projection = self.alt_projection
        else:
            projection = self.projection
            
        # sets up map
        mp = Basemap(projection=projection, ax=ax, **proj_kwargs)
        mp.drawcoastlines()
    
        if self.map_grid:
            parallels = np.arange(lat[-1], lat[0], self.par_deg)
            meridians = np.arange(lon[0], lon[-1], self.mer_deg)
            mp.drawparallels(parallels)
            mp.drawmeridians(meridians) 
        
        mp.drawmapboundary()
        
        # Maps lats and lons to x and y coordinates in the mp object
        # Credit goes to Ronan Lamy
        # might need to be moved out of function
        if projection in ['cyl']:
            mg = mp.imshow(im, norm=self.norm, cmap=self.cmap, interpolation = "nearest")
        else:
            x, y = mp(*np.meshgrid(lon[:], lat[:]))
            mg = mp.pcolor(x, y, im, norm=self.norm, cmap=self.cmap, ax=ax)
        return 
    
    def get_norm(self, im, bounds):
        """ Determines the value distribution of the data 
            for the colormap by mapping the data to a 0-1 scale.  
        """
        # can replace self with cmap and make this a general function
        if bounds:
            vmin, vmax = bounds
        else:
            vmin, vmax = im.min(), im.max()
        
        # should just use above
        if not np.isfinite(vmax).all():
            vmax = np.nan_to_num(vmax)
            
        if not np.isfinite(vmin).all():
            vmin = np.nan_to_num(vmin)
            
        if self.center:
            vmax = max(vmax, np.abs(vmin))
            vmin = vmax * -1
            
        log.debug("norm: vmin={:.3}, vmax={:.3}".format(vmin, vmax))
        if self.discrete:
            return discrete_norm(vmin, vmax, self.cmap)
        return matplotlib.colors.Normalize(vmin, vmax)    
    
    def get_colorbar(self, ax, im):
        """Returns a colorbar. 
        """
        
        # creates a new axis for the colorbar based off of axis
        # tries to ensure that the colorbar will be proportional 
        # to the axis
       
        divider = mpl_toolkits.axes_grid.make_axes_locatable(ax) 
        if self.orientation == 'vertical':
            cax = divider.new_horizontal(size="5%", pad=0.05, axes_class=matplotlib.axes.Axes) 
            cbaxis = 'y'
            
        elif self.orientation == 'horizontal':
            cax = divider.new_vertical(size="5%", pad=0.25, pack_start=True,axes_class=matplotlib.axes.Axes)
            cbaxis = 'x'
            
        fig = ax.figure
        fig.add_axes(cax)                        
        
        formatter = matplotlib.ticker.ScalarFormatter(useMathText=True)
        formatter.set_scientific(True)
        formatter.set_powerlimits((-3,4))
        
        cb = matplotlib.colorbar.ColorbarBase(cax, cmap=self.cmap, norm=self.norm, 
                                              orientation = self.orientation, format=formatter)
        return cb

    def set_labels(self, ax, cb, **kwargs):
        """Sets the labels based on the object, function, or data labels
        """
        
        log.debug("Label kwargs: {!r}".format(kwargs))
        # Maps the object keys to the dataobj keys
        graph_data = [('title', 'dataset'), 
                      ('cblabel', 'variable'),
                      ('ylabel', 'latitude'), 
                      ('xlabel', 'longitude'),
                      ('freq', 'time_units')]
       
        labels = self.get_labels(graph_data, kwargs)
        
        if 'time' in kwargs:
            add_time_to_label(kwargs['time'], labels, 
                              self.dtime, self.time_units)
        
        ccpgraph.labelgraph(ax=ax, cb=cb, labels=labels)
        
        
def add_time_to_label(time, labels, dtime = None, units=None):
    """Inserts time into title.
    """
    
    ti = ccpgraph.timestr_ind(labels['freq'])
    
    # builds individual time strings 
    if 'start' in time:
        start = indices.create_start_time(time['start'])
    elif dtime:
        start = coards.from_udunits(dtime[0], units)
    else:
        start = None
    if start:
        start_str = start.isoformat()[:ti]
    
    if 'end' in time:
        end = indices.create_end_time(time['end'])
    elif dtime:
        end = coards.from_udunits(dtime[1], units)
    else:
        end = None
    if end:
        end_str = end.isoformat()[:ti]
    
    # Organizes the time string
    if start_str and not end_str:
         timestr = "from {}".format(start_str)
    elif end_str and not start_str:
         timestr = " until {}".format(end_str)
    elif start_str == end_str:
        timestr = "at {}".format(start_str)
    else:
        timestr = "from {} to {}".format(start_str, end_str)
    
    # adds the string to the title
    labels['title'] = "{}\n{}".format(labels['title'], timestr)
    return

def calc_bounds(imrange):
    """Picks the optimum increment for the image""" 
    if imrange == 0:
        place = 1
    else:
        place = int(np.log10(imrange))
    MIN_STEPS = 15
    for inc in [10, 5, 1, 0.5, 0.1, 0.05, 0.01, 0.005, 0.001]:   
        if np.floor(place)>0:
            inc = inc * (10**place)
        steps = int(imrange)/inc
        if steps%2!=1: 
            steps += 1
        if steps>MIN_STEPS:
            break
    return inc, steps
  
def discrete_norm(vmin, vmax, cmap):
    """Calculates the bins for the discrete norm
    """
    #needs overwrite for countours 
    inc, steps = calc_bounds(vmax-vmin)
    vn_pl = np.floor(np.log10(vmin))
    vx_pl = np.floor(np.log10(vmax))
    
    print "vmin: {} vmax: {}".format(vmin, vmax)
    if np.isfinite(vn_pl):
        vmin = np.round(vmin, int(vn_pl))

    if np.isfinite(vx_pl):
        vmax = np.round(vmax, int(vx_pl))
    
    print "new vmin: {}, vmax: {}".format(vmin, vmax)
    
    boundaries = np.arange(vmin, vmax, inc)
    print "bounds: {}".format(boundaries)
    
    if len(boundaries)<steps:
        boundaries = np.linspace(vmin, vmax, steps)
        print "new bounds: {}".format(boundaries)
        
    return matplotlib.colors.BoundaryNorm(boundaries, cmap.N)
