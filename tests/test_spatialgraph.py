#!/usr/bin/env python
#
# test_spatialgraph.py
#
# Hannah Aizenman, 2011-07
# 
# http://www.opensource.org/licenses/bsd-license.php

"""Tests the spatial graph class and methods
"""

__docformat__ = "restructuredtext"

# http://docs.python.org/2.7/library/os.html
import os
# http://docs.python.org/2.7/library/unittest.html
import unittest

# http://docs.scipy.org/doc/numpy-1.6.0/user/
import numpy as np

from ccplib.datahandlers import unpack
from ccplib.visualization import spatial
from ccplib.algorithms import statistics
class Gistemp(unittest.TestCase):
    """test class for gistemp
    """
    def setUp(self):
        file_path = '../data/fields/gistemp_sat_anom_2.5deg.nc'
        save_path = os.path.join(os.getcwd(), "gistemp")
        field = 'field'
        self.data_obj = unpack.fromNetCDF(file_path, field = field,
                   save_path=save_path, scrnlog=False, overwrite=False)
        self.graph_obj = spatial.SpatialGraph(self.data_obj)
        self.graph_obj.cmap = 'gist_ncar'
        self.missing = self.data_obj.missing_value
        self.time_range = dict(start=[1938,5], end=[1938,5])
        self.im = self.data_obj.get_all_data(time_range=self.time_range)
        
    def tearDown(self):
        del self.data_obj
        del self.graph_obj
        del self.im
        
    def test_obj(self):
        self.assertIsInstance(self.graph_obj, spatial.SpatialGraph)
        
    def test_simple(self):
        #tests whether I can create a graph at all
        im = np.random.random((100,100))
        self.graph_obj.colorbar = False
        self.graph_obj.ccpfig(im, "random_im")
        
    def test_basic(self):
        self.graph_obj.colorbar = False
        self.graph_obj.ccpfig(self.im, 'gis_plain_fig')

    def test_merc(self):
        self.graph_obj.projection = 'merc'
        self.graph_obj.map_grid = False
        self.graph_obj.colorbar = False
        self.graph_obj.ccpfig(self.im, 'gis_merc')
             
    def test_robin_wcb(self):
        self.graph_obj.projection = 'robin'
        self.graph_obj.ccpfig(self.im, 'gis_robin')

    @unittest.skip("will implement later")
    def test_omerc(self):
        self.graph_obj.projection = 'omerc'
        self.graph_obj.colorbar = False
        self.graph_obj.ccpfig(self.im, 'gis_omerc')
    
    def test_cb_basic(self):       
        self.graph_obj.ccpfig(self.im, 'gis_cb_nomap')
        
    def test_mean_cb(self):
        im = self.data_obj.get_all_data()
        masked = statistics.mean(self.data_obj, im)
        #self.graph_obj.center = True
        self.graph_obj.ccpfig(masked, 'gismeancb_nomap')
        
    def test_centered(self):
        im = self.data_obj.get_all_data()
        masked = statistics.mean(self.data_obj, im)
        self.graph_obj.center = True
        self.graph_obj.projection = 'mill'
        labels = dict(alg_name = "mean")
        self.graph_obj.ccpfig(masked, 'gismean_mill_meancen',
                              labels=labels)
        
    def test_label_wcb(self):
        self.graph_obj.title = 'gistemp_sat_anom_2.5deg'
        self.graph_obj.xlabel = 'longitude'
        self.graph_obj.ylabel = 'latitude'
        self.graph_obj.cblabel = 'temperature'
        self.graph_obj.ccpfig(self.im, 'gis_label_cb_nm')
        
    def test_label_map(self):
        self.graph_obj.projection = 'cyl'
        self.graph_obj.title = 'gistemp_sat_anom_2.5deg'
        self.graph_obj.xlabel = 'longitude'
        self.graph_obj.ylabel = 'latitude'
        self.graph_obj.cblabel = 'temperature'
        self.graph_obj.ccpfig(self.im, 'gis_label_map')
    
    def test_full_graph(self):
        self.graph_obj.projection = 'moll'
        self.graph_obj.title = 'gistemp_sat_anom_2.5deg'
        self.graph_obj.xlabel = 'longitude'
        self.graph_obj.ylabel = 'latitude'
        self.graph_obj.cblabel = 'temperature anomoly'
        labels = dict(time=self.time_range)
        self.graph_obj.ccpfig(self.im, 'gis_full', 
                              labels=labels)
        

    def test_restricted(self): 
        coords = dict(top=61.0, bottom=-61.0, left=91.0, right=271.0)
        time_range =  dict(start=[1938,5], end=[1938,5])
        im = self.data_obj.get_all_data(coords=coords, 
                                        time_range=time_range)
        self.graph_obj.projection = 'robin'
        self.graph_obj.alt_projection = 'merc'
        labels = dict(time=time_range)
        self.graph_obj.ccpfig(im, 'gis_full_rest', 
                              coords = coords, labels=labels)
                                 
    def test_label_args(self):
        self.graph_obj.projection = 'cyl'
        labels = dict(title = 'gistemp_sat_anom_2.5deg',
                      xlabel = 'longitude',
                      ylabel = 'latitude',
                      cblabel = 'temperature',
                      time = self.time_range,
                      freq = self.data_obj.time_units)
        self.graph_obj.ccpfig(self.im, 'gis_label_func', 
                              labels=labels)

        
        
if __name__ == '__main__':
    unittest.main()