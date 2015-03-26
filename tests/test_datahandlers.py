#!/usr/bin/env python
#
# test_datahandlers.py
#
# Hannah Aizenman, 2011-06
#
# http://www.opensource.org/licenses/bsd-license.php

"""Tests various data extraction methods in datahandlers
"""

__docformat__ = "restructuredtext"

# http://docs.python.org/2.7/library/os.html
import os
# http://docs.python.org/2.7/library/unittest.html
import unittest

# http://docs.scipy.org/doc/numpy-1.6.0/user/
import numpy as np


import ccplib
from ccplib.datahandlers import unpack, ccpdata

class Gistemp(unittest.TestCase):
    """test class for gistemp
    """
    def setUp(self):
        file_path = '../data/fields/gistemp_sat_anom_2.5deg.nc'
        save_path = os.path.join(os.getcwd(), "gistemp")
        field = 'field'
        self.obj = unpack.fromNetCDF(file_path, field = field, 
        save_path=save_path, scrnlog=False, overwrite=False)
       
    def tearDown(self):
        del self.obj
   
    def test_obj(self):
        self.assertIsInstance(self.obj, ccpdata.CCPData)
    
    @unittest.skip("stub, will implement later")
    def test_rpr(self):
        #not quite sure what I should implement/how to test this
        pass
        
    def test_unpack(self):
        """ tests if DataAPI returns an object for the gistemp file """
        self.assertEqual(self.obj.file_type, 'netcdf')
    
    @unittest.skip("broken because of selection, will fix later")
    def test_getdata(self):
        """tests that the getdata function works"""
        data = self.obj.extract_func(self.obj.file_path)
        self.assertIsNotNone(data)

    def test_reshape(self):
        """tests that reshape works"""
        data_reshape = (self.obj.shape[0] ,self.obj.shape[1]*self.obj.shape[2])
        data = self.obj.get_all_data(data_reshape = data_reshape)
        self.assertEqual(data.shape, data_reshape)
        
    def test_reshape_meth2(self):
        """tests that reshape works"""
        data_reshape = (self.obj.shape[0] ,self.obj.shape[1]*self.obj.shape[2])
        data = self.obj.get_all_data(data_reshape = ('time', 'latlon'))
        self.assertEqual(data.shape, data_reshape)
                                              
    def test_get_all_data(self):
        """ tests that the get_all_data function works""" 
        data = self.obj.get_all_data()
        self.assertEqual(data.shape, self.obj.shape)
        
    def test_coord(self):
        coords = dict(top=61.0, bottom=-61.0, left=91.0, right=271.0)
        test_shape = (1576, 62, 91)
        data = self.obj.get_all_data(coords=coords)
        self.assertEqual(data.shape, test_shape)
    
    def test_cons(self):
         coords = dict(top='61N', bottom='61S', left='91', right='271')
         test_shape = (1576, 62, 91)
         data = self.obj.get_all_data(coords=coords)
         self.assertEqual(data.shape, test_shape)

    def test_cons_mix(self):
        coords = dict(top='61N', bottom='61S', left=91, right=271)
        test_shape = (1576, 62, 91)
        data = self.obj.get_all_data(coords=coords)
        self.assertEqual(data.shape, test_shape)
                                    
    def test_time(self):
        time_range = dict(start=[1913, 5, 1], end=[1971, 9, 1]) 
        test_shape =(701, 90, 180)
        data = self.obj.get_all_data(time_range=time_range)
        self.assertEqual(data.shape, test_shape)
    
    def test_time_default(self):
        time_range = dict(start=[1913, 5], end=[1971, 9])
        test_shape =(701, 90, 180)
        data = self.obj.get_all_data(time_range=time_range)
        self.assertEqual(data.shape, test_shape)
        
    def test_single_time(self):
        time_range = dict(start=[1938,5], end=[1938,5])
        test_shape = (90, 180)
        data = self.obj.get_all_data(time_range=time_range)
        self.assertEqual(data.shape, test_shape)

    def test_coord_time(self):
        coords = dict(top=61.0, bottom=-61.0, left=91.0, right=271.0)
        time_range = dict(start=[1913, 5], end=[1971, 9])
        test_shape = (701, 62, 91)
        data = self.obj.get_all_data(time_range=time_range, 
                                      coords=coords)
        self.assertEqual(data.shape, test_shape)
        
    def test_all_selection_ops(self):
        coords = dict(top=61.0, bottom=-61.0, left=91.0, right=271.0)
        time_range = dict(start=[1913, 5], end=[1971, 9])
        data_reshape = ('time', 'latlon')
        data = self.obj.get_all_data(time_range=time_range, 
                  coords=coords, data_reshape=data_reshape)
        self.assertEqual(data.shape, (701, 62*91))

class ccsm_c(unittest.TestCase):
    """test class for ccsm_c
    """
    def setUp(self):
        file_path = '../data/fields/ccsm-c.cdf'
        field = 'field'
        save_path = os.path.join(os.getcwd(), "ccsm")
        self.obj = unpack.fromNetCDF(file_path, field = field,
        save_path = save_path, scrnlog=False, overwrite = False)
                                                  
    def test_obj(self):
        self.assertIsInstance(self.obj, ccpdata.CCPData)
        
    def test_unpack(self):
        """ tests if DataAPI sets attributes correctly """
        self.assertEqual(self.obj.file_type, 'netcdf')
    
    @unittest.skip("broken because of selection, will fix later")    
    def test_getdata(self):
        """tests that the getdata function works"""
        data = self.obj.extract_func(self.obj.file_path)
        self.assertIsNotNone(data)
        
    def test_get_all_data(self):
        """ tests that the get_all_data function works"""
        data = self.obj.get_all_data()
        self.assertIsNotNone(data)
        

class mann(unittest.TestCase):
    """
    test cases for mann2008 set
    """
    def setUp(self):
        """
        sets up working mann data obj
        """
        self.file_path = '../data/proxy_db/mann2008infilled.nc'
        save_path = os.path.join(os.getcwd(), 'mann')
        field = 'proxy'
        self.obj = unpack.fromNetCDF(self.file_path, field = field, 
        save_path = save_path, scrnlog = False, overwrite = False, 
        gridded = False)
        
    def test_obj(self):
        self.assertIsInstance(self.obj, ccpdata.CCPData)
        
    def test_unpack(self):
        """ tests if DataAPI returns an object for the gistemp file """
        self.assertEqual(self.obj.file_type, 'netcdf')
    
    @unittest.skip("broken because of selection, will fix later")
    def test_getdata(self):
        """tests that the getdata function works"""
        data = self.obj.extract_func(self.obj.file_path)
        self.assertIsNotNone(data)
        
    def test_get_all_data(self):                            
        """ tests that the get_all_data function works"""
        data = self.obj.get_all_data()
        self.assertEqual(data.shape, self.obj.shape)
        
    @unittest.skip("stub, need to write test later")
    def test_coords(self):
        coords = dict(top=61.0, bottom=-61.0, left=91.0, right=271.0)
        test_shape = (1576, 62, 91)
        data = self.obj.get_all_data(coords = coords)
        self.assertEqual(data.shape, test_shape)
        
    @unittest.skip("stub, will implement later")
    def test_folder_unpack(self):
        """tests that get data all can work with folders
        not totally functional at this point
        more likely to be worked into selection code/test
        """
        folder_path = '../data/proxy_db'
        field = 'proxy'
        ccp_obj = unpack.fromNetCDF(folder_path, field = field)
        ccp_data = ccp_obj.get_all_data()
        print "mann size", ccp_data.size

    
if __name__ == '__main__':
    unittest.main()