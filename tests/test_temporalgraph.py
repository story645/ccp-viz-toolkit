#!/usr/bin/env python
#
# test_temporalgraph.py
#
# Hannah Aizenman, 2011-08
#
# http://www.opensource.org/licenses/bsd-license.php

"""Tests the temporal graph class and methods
"""

__docformat__ = "restructuredtext"

# http://docs.python.org/2.7/library/os.html
import os
# http://docs.python.org/2.7/library/unittest.html
import unittest

# http://docs.scipy.org/doc/numpy-1.6.0/user/
import numpy as np

from ccplib.datahandlers import unpack
from ccplib.visualization import temporal
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
        self.graph_obj = temporal.TemporalGraph(self.data_obj)
        self.graph_obj.cmap = 'gist_ncar'
        self.coords = dict(top=41, bottom=41, left=73, right=73)
        self.im = self.data_obj.get_all_data(coords=self.coords)
        
    def tearDown(self):
        del self.data_obj
        del self.graph_obj
        del self.im
        
    def test_obj(self):
        self.assertIsInstance(self.graph_obj, temporal.TemporalGraph)
        
    def test_simple(self):
        #tests whether I can create a graph at all
        im = np.random.random((100))
        self.graph_obj.ccpfig(im, "random_im", xdata=range(100))

    def test_basic(self):
        self.graph_obj.ccpfig(self.im, 'gis_plain_fig')
    
    def test_label(self):
        labels = dict(location=self.coords)
        self.graph_obj.ccpfig(self.im, 'gis_lab', labels=labels)
        
    def test_water(self):
        coords = dict(top=89, bottom=89, left=1, right=1)
        im = self.data_obj.get_all_data(coords=coords)
        self.graph_obj.ccpfig(im, 'gis_water_fig')
        
    def test_restricted_time(self):
        labels = dict(location=self.coords)
        time_range = dict(start=[1915,03,01], end=[1880,01,01])
        im = self.data_obj.get_all_data(coords=self.coords,
                                        time_range=time_range)
        self.graph_obj.ccpfig(im, 'ccsm_lab_rest', labels=labels,
                              time_range=time_range)
                                                                                                              
        
class ccsm_c(unittest.TestCase):
    """test class for ccsm_c
    """
    def setUp(self):
        file_path = '../data/fields/ccsm-c.cdf'
        field = 'field'
        save_path = os.path.join(os.getcwd(), "ccsm")
        self.data_obj = unpack.fromNetCDF(file_path, field = field,
        save_path=save_path, scrnlog=False, overwrite=False)
        self.graph_obj = temporal.TemporalGraph(self.data_obj)
        self.graph_obj.cmap = 'gist_ncar'
        self.coords = dict(top=42.5, bottom=42.5, left=82.5, right=82.5)
        self.im = self.data_obj.get_all_data(coords=self.coords)
    
    def test_label(self):
        labels = dict(location=self.coords)
        self.graph_obj.ccpfig(self.im, 'ccsm_lab', labels=labels)
                            
    def test_restricted_time(self):
        labels = dict(location=self.coords)
        time_range = dict(start=[1497,07],end=[1764,07])
        im = self.data_obj.get_all_data(coords=self.coords, 
                                        time_range=time_range)
        self.graph_obj.ccpfig(im, 'ccsm_lab_rest', labels=labels, 
                              time_range=time_range)
        
        
        
if __name__ == '__main__':
    unittest.main()