#!/usr/bin/env python
#
# unpack.py
#
# Hannah Aizenman, 2011-06
#
# http://www.opensource.org/licenses/bsd-license.php

"""
A collection of helper functions that parse the metadata of the files, 
passing the information to the ccpdata constructor. Support for new filetypes
should be added to this file and as an extract method in ccpdata.py
"""

__docformat__ = "restructuredtext"

# http://docs.python.org/2.7/library/os.html#module-os
import os
# http://docs.python.org/2.7/library/logging.html#module-logging
import logging

import ccplib.misc.utils
from ccplib.datahandlers import ccpdata

log = logging.getLogger(ccplib.misc.utils.LOGNAME)

def get_unpack_func(file_type):
    """
    Returns an unpack function given a filetype
    :Param file_type:
        file type of the data (netcdf, hdf5, etc)
    :Return extract_func:
        function for extracting data
    """
    if file_type.lower() == 'netcdf':
        return fromNetCDF
    else:
        raise TypeError("file type not supported")

def fromNetCDF(file_path, **kwargs):    
    """Extracts data attributes from netcdf header information
    and then passes those attributes to a ccpobj. 
    
    :Param file_path:
        Path to the file or a folder of files.
    :Param kwargs:
        :Param name:
            Name of the dataset
        :Param field:
            The type of data, e.g. field or proxy.
        :Param gridded:
            Data is gridded (latXlon) -default is True
        :Param lat_key:
            Name of the latitude field in the input file. 
        :Param lon_key:
            Name of the longitude field in the input file. 
        :Param time_key:
            Name of the time field in the input file. 
        :Param data_key:
            Name of the data field in the input file. 
        :Param scrnlog:
            Prints the log to console. The default is True.
        :Param txtlog:
            Writes the log to a text file. The default is True. 
        :Param save_path:
            The folder the output is saved to.
        :Param create_folder:
            Create a folder for the output (default is True)
        :Param overwrite:
            Overwrite existing output folder, thereby deleting all 
            its contents. The default is False.
        :Param variable:
            Name of the variable in the data field (used in labels)
        :Param latitude:

            Name of the x dimension
        :Param longitude:
            Name of the y dimension
        :Param time:
            Name of the time dimension
    :Return:
        A CCPData object containing information about the data.
    """    
    
    # Sets up logging and default path.
    save_path = kwargs.get('save_path', 
                            os.path.join(os.getcwd(), 'output'))
    overwrite = kwargs.get('overwrite', False)
  
    scrnlog = kwargs.get('scrnlog', True)
    txtlog = kwargs.get('txtlog', True)
    create_folder = kwargs.get('create_folder', True)
    if create_folder:
        ccplib.misc.utils.create_folder(save_path, overwrite)
    
    ccplib.misc.utils.setup_logging(save_path, scrnlog=scrnlog, txtlog=txtlog)
    
    folder = os.path.isdir(file_path)
    multifile = False
    if folder or '*' in file_path:
        if folder:
            file_list =  [os.path.join(file_path, fl) for fl in os.listdir(file_path)]
            file_path = file_list
        multifile = True
        
    open_nc, lib = ccpdata.netcdf_open(multifile)
    
    if open_nc and lib:
        log.debug("ccpdata object handles info for: {}".format(file_path))
        nc_data = open_nc(file_path, 'r')   
    else:
        error_str = "invalid input: {} is not supported"
        raise Exception(error_str.format(file_path))
        
    meta_fields = nc_data.variables.keys()
    log.debug("meta_fields: {!r}".format(meta_fields))
    
    cname = get_common_dim_names()
    
    # Code defers to user provided name when possible.
    lat_key = kwargs.get('lat_key', 
			get_field_name(meta_fields, cname['lat']))
    lon_key = kwargs.get('lon_key', 
			get_field_name(meta_fields, cname['lon']))
    time_key = kwargs.get('time_key', 
			get_field_name(meta_fields, cname['time']))
    
    # Returns the field instances named by each key
    nc_field = nc_data.variables
    lat = nc_field[lat_key]
    lon = nc_field[lon_key]
    time = nc_field[time_key]
    
    # Extracts data_key and data field.
    data_dims = [lat.shape, lon.shape, time.shape]
    data_key = kwargs.get('data_key', 
			get_data_field(nc_field, data_dims))
    data_field = nc_field[data_key]

    # Extracts the names of various fields
    labels = {}
    if hasattr(data_field, 'dataset'):
        labels['dataset'] = data_field.dataset
    elif 'name' in kwargs:
        labels['dataset'] = kwargs['name'].upper()
    else:
        if multifile:
            filename = os.path.split(file_path[0])[-1]
        else:
            filename = os.path.split(file_path)[-1]
        labels['dataset'] = filename.split('.')[0].upper()
    
    fields = [('variable', data_field), ('latitude', lat), 
              ('longitude', lon), ('time', time)]
    
    for key, field in fields: 
        if hasattr(field, 'long_name') and hasattr(field, 'units'):
            labels[key] = "{} ({})".format(field.long_name, field.units)
        elif hasattr(field, 'long_name'):
            labels[key] = field.long_name
        elif key in kwargs:
            labels[key] = kwargs[key]
        elif key == 'variable':
            labels[key] = data_key.capitalize()
        else:
            labels[key] = key.capitalize()
            
        if hasattr(field, 'units') and field.units not in labels[key]:
            labels[key] = "{} ({})".format(labels[key], field.units)
        
    
    # Initial attributes of the ccpdata object
    data_vals = dict(file_path=file_path,
                     lat=lat[:],
                     lon=lon[:],
                     time=time[:],
                     file_type='netcdf',
                     data_key=data_key, 
                     time_units=time.units,
                     shape=data_field.shape, 
                     save_path=save_path,
                     labels = labels,
                     multifile = multifile
                     )
                     
    data_vals['gridded'] = kwargs.get('gridded', True)
    # Extracts various params that don't show up in all netcdf files 
    for key in ['add_offset', 'scale_factor', 'missing_value']:
        if hasattr(data_field, key):
            data_vals[key] = getattr(data_field, key)
 
    nc_data.close()
    
    # Creates the ccpdata object
    return ccpdata.CCPData(**data_vals)
 
def get_common_dim_names():
    """list of common names for various netcdf dimensions
    """
    # add new names as needed
    common_names = dict( lat = ['latitude', 'lat', 'y'],
                         lon = ['longitude', 'lon', 'x'],
                         time = ['time', 't']
                         )
    return common_names

def get_field_name(nc_field_keys, common_field_keys):
    """
    Compares the netcdf fields in the input file against
    a list of common names for each dimension (field). The user 
    should input the key(field name) if the method fails due to 
    multiple or no keys being found. 
    
    :Param nc_field_keys:
        The field names in the input file.
    :Param common_field_keys:
        A list of common names for a dimension. 
    :Return field_name:
        The name used by the input file.
    """
    # searches through all the keys in the file
    # returns any that are in the list of common names
    # lower is used to provide case insensitivity.
    field_names = [key for key in nc_field_keys 
                        if key.lower() in common_field_keys]
    log.debug("keys found: {!r}".format(field_names))
    return field_names[0]  

def get_data_field(nc_fields, data_dims):
    """Finds the key for the data field by finding any fields that 
    have dimensions of lat, lon, and time. If multiple keys are found, 
    logs key names. 
    :Param nc_fields:
        A dictionary of the fields in the netcdf file.
    :Param data_dims:
        A list of the shapes of the dimensions the data should have.
    :Return data_key_list[0]:
        Returns the first found key.
    """
    # The dim is either a 1d row or column.
    # Extracts the dimensions from the list of dimension shapes.
    data_dim = set(d[0] for d in data_dims)
    # May have to add in support for extracting from rows
    data_key_list = []
    for key in nc_fields:
        if hasattr(nc_fields[key],'shape'):
            if data_dim.issubset(nc_fields[key].shape):
                data_key_list.append(key)
    log.debug("fields found: {!r}".format(data_key_list))
    return data_key_list[0]                                

