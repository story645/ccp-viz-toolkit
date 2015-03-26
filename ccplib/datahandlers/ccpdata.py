#!/usr/bin/env python
#
# ccpdata.py
#
# Hannah Aizenman, 2011-06
# 
# http://www.opensource.org/licenses/bsd-license.php

"""This module builds the CCPData object.
The ccpdata object contains metadata and has methods 
for extracting data from its container file. 
"""

__docformat__ = "restructuredtext"

# http://docs.python.org/2.7/library/os.html#module-os
import os
# http://docs.python.org/2.7/library/logging.html
import logging
# http://docs.scipy.org/doc/numpy-1.6.0/reference/
import numpy as np
# collection of mantainance functions 
# (e.g. log and folder creation) 
import ccplib.misc.utils

from ccplib.datahandlers import indices

log = logging.getLogger(ccplib.misc.utils.LOGNAME)

class CCPData(object):
    """Returns an object containing attributes of the data and 
    extraction methods for the data.
    Required:     
        :Param file_path: 
            The location of either the data file or 
            the folder containing the data files.   
        :Param file_type:
            The file type of the file (e.g. netcdf, dat, mat).
    kwargs:
        :Param field: 
            The description of the data type 
            (e.g. field, proxy, etc.).
        :Param time: 
            Array of timestamps of the observations in the data.
        :Param time_units:
            A string  of the form 'time units since reference time' 
        :Param lat:
            Array of latitude locations of the observations in the data.
        :Param lon:
            Array of longitude locations of the observations in the data.
        :Param gridded:
            data is gridded (latXlon) (default True)
        :Param data_key:
            The netcdf field name of the variable.
        :Param add_offset: 
            The offset for packed data.
        :Param scale_factor: 
            The scale factor for packed data.   
        :Param save_path:
            The path to the folder in which to save the output.
        :Param shape:
            The shape of the array in the file. 
        :Param multifile:
            Bool - True if data is spread over multiple files, default is False
        :Param labels:
            dict containing the (key, discriptive name) of each dimension
            keys: 'variable', 'latitude', 'longitude', 'time', 'dataset'
    :Return:
        A CCPData object containing information about the data.
    
    """
    
    def __init__(self, **kwargs):
        """Builds an object containing properties of the data. 
        This function is generally accessed using a helper function 
        in unpack.py.
        
        """
        # New datatypes should be supported by adding 
        # a function to unpack.py and an extract method to CCPData. 
       
        self.__dict__.update(kwargs)
        
        self.gridded = kwargs.get('gridded', True)
        self.multifile = kwargs.get('multifile', False)
        # The formula for packed data is:
        # data = packed_data*scale_factor + add_offset
        self.add_offset = kwargs.get('add_offset', 0)
        self.scale_factor = kwargs.get('scale_factor', 1)
        
        # returns a function for extracting the data 
        # based on the file type
        extract_func = self.get_extract_func()
        self.extract_func = extract_func
        log.debug("CCPData object created")
           
    def __repr__(self):
        return "<{0!s}({1!r})>".format(self.__class__,self.__dict__)
  
    def get_all_data(self, file_list=None, concat_dim=-1, **kwargs):
        """Builds a numpy array out of all the data. 
        :Param file_list:
            An optional list of files to extract from the file_path 
            if the file_path points to a folder. The default is that
            all files in the file path folder will be extracted
        :Param concat_dim:
            The dimension along which multiple files are stacked.
            The default is to concatenate along the last dimension.
        :Param data_reshape:
            Preferred shape of the data (default is the same shape as on disk)
            can also be specified as ('time', 'latlon')
        :Param coords:
            Dictionary containing the region to restrict the data to:
                top: Northernmost latitude
                bottom: Southernmost latitude
                left: Westernmost longitude
                right: Easternmost longitude
        :Param time_range:
            Dictionary containing the time to restrict the data to:
                start: [year, *args]
                end: [year, *args]
                *args = month, day, hour, minute, second, microsecond
                Time is organized: distant(start) to recent(end)
                Defaults to the first and last observation in
                The dataset, year, month, respectively
                used to create a python datetime object:
                http://docs.python.org/2.7/library/datetime.html
        :Param height:
            array of pressure of values

        """
        # Note: This function can/should be parallelized
        
        # Empty dicts are to allow for iteration
        # Gets the indices for a bounded region
        
        
        coords = kwargs.get('coords', dict())
        time_range = kwargs.get('time_range', dict())
        data_reshape = kwargs.get('data_reshape')
        data_kw = dict(coords=coords, time_range=time_range, data_reshape=data_reshape)
        # Tries to pull data from whatever the file_path points to.
        return self.extract_func(self.file_path, **data_kw)
        
    def get_data(self, file_obj, time_range, coords, **kwargs):
        """Extracts data from a single file. 
        :Param file_obj:
            Pointer to the data on disk
        :Param data_reshape:
            The preferred shape for the data after extraction.
            Can also be specified as ('time', 'latlon')
        :Param coords:
            Dictionary containing the region to restrict the data to
        :Param time_range:
            Dictionary containing the time to restrict the data to
        Note: see get_all_data docs for more detailed discription of coords and time_range
        :Param height:
            indices of selected height range if data has height (default is none)
        :Return data:
            The function returns the data as a numpy array.
        Note: This function assumes time is the first dimension
        
        """
        
        log.debug("file on disk shape: {}".format(self.shape))

        height = kwargs.get('height', Ellipsis)
        data = self.get_slice(file_obj, time_range, coords, height)
        
        log.debug("extracted data shape: {}".format(data.shape))
        
        # shrinks data to 
        data = np.squeeze(data)
        
        data_reshape = kwargs.get('data_reshape')
        
        if data_reshape:
            if data_reshape == ('time', 'latlon'):
                data_reshape = (data.shape[0], -1)
            data.shape = data_reshape
            log.debug("data reshaped, new shape: {}".format(data.shape))
            
        # Unpacks data or data*1+0 by default
        data = self.add_offset +  (data * self.scale_factor)
        
        # wraps a single digit in an array to keep return consistent 
        if not isinstance(data, np.ndarray):
            data = np.array([data])
        return data
   
    def extract_netcdf(self, extract_path, **kwargs):
        """Extracts netcdf files using python-netCDF4, 
        falls back to scipy.io if netcdf4 isn't present
        handles direct i/o clean up. 
        :Param extract_path:
            The path of the data to be extracted.
        :Param **kwargs:
            Passed directly to get_data (lat_lon, time, data_reshape)
        
        """
        
        open_nc, lib = netcdf_open(self.multifile)
        nc_data = open_nc(extract_path, 'r')
        file_obj = nc_data.variables[self.data_key]
        data = self.get_data(file_obj, **kwargs)
        nc_data.close()
        return data
             
    def get_slice(self, file_obj, time_range, coords, height=Ellipsis):
        """Slices data assuming scipy.io is used to handle data, 
        makes use of numpy fancy indexing and relies on converting args to inds
        :Param file_obj:
            Pointer to the data on disk
        :Param time_range:
            Dictionary containing the time to restrict the data to
            Note: see get_all_data docs for more detailed discription of coords and time_range
        :Param coords:
            Dictionary containing the region to restrict the data to
        :Return: 
            user selected subset of the data
        """
        time = indices.time_to_slice(self.time, self.time_units, time_range)
        lat_lon = indices.coord_to_inds(self.lat, self.lon, coords, self.gridded)
        if height != Ellipsis:
            height_ind = height_to_slice(self.height, height)
    
        #assumes time is the first index
        inds = [time]
        
        #need a none shape based way to do this
        if len(self.shape)==4:
            #assumes height/depth is the second dim
            inds.append(height_ind)
        if self.gridded:
            (lat, lon) = lat_lon
            inds.append(lat)
            inds.append(lon)
        elif len(self.shape) == 2:
            inds.append(lat_lon)
        else:
            # This should probably be a different type of error
            raise ValueError("unhandled dimension")
        
        return file_obj[tuple(inds)]
    
    def get_extract_func(self):
        """Returns a function to extract the data 
        based on the data's file type.
        
        """
        if self.file_type == 'netcdf':
            return self.extract_netcdf
        else:
            return Warning("Type not supported")
 
        
def netcdf_open(multifile=False):
    """Return function for opening file based on which library
    is installed
    """
    try: 
        #import pyngl
        import netCDF4
        if multifile:
            return netCDF4.MFDataset, 'netCDF4'
        return netCDF4.Dataset, 'netCDF4'
    except ImportError, e:                                                     
        import scipy.io.netcdf as nc                                           
        return nc.netcdf_file, 'scipy.io'                                      
        
