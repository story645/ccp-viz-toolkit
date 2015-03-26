#!/usr/bin/env python
#
# demo_gis.py
#
# Hannah Aizenman, 2011-07-11

"""Example of using ccplib"""

__docformat__ = "restructuredtext"

# http://docs.scipy.org/doc/numpy-1.6.0/user
import numpy as np

from ccplib.datahandlers import unpack
from ccplib.visualization import spatial

def main():
    """
    This script is a demo of how to use the ccplib 
    datahandler and visualization libraries.
    """
    
    # create data object
    file_path = '../data/fields/gistemp_sat_anom_2.5deg.nc'
    data_obj = unpack.fromNetCDF(file_path, field = 'field')
    
    # get data
    image = data_obj.get_all_data()
    
    # do some math on the data and return the image to plot
    im_masked = np.ma.masked_equal(image, data_obj.missing_value)
    masked = im_masked.std(0)
    
    # set up graph attributes
    graph_attrs = dict( projection = 'moll', 
                        title = 'gistemp_sat_anom_2.5deg',
                        cmap = 'gist_heat_r',
                        xlabel = 'longitude',
                        ylabel = 'latitude',
                        cblabel = 'std dev of temp anomalies')
    
    # create the object
    graph_obj = spatial.SpatialGraph(data_obj, **graph_attrs)
    
    # make a graph
    graph_obj.ccpfig(masked, image_name = 'gistemp_demo')
    
if __name__ == '__main__':
    main()