#!/usr/bin/env python
#
# tasks.py
#
# Hannah Aizenman, 2011-08

"""Interface between ccplib and views"""

__docformat__ = "restructuredtext"

# http://docs.python.org/library/re.html 
import re
# http://docs.python.org/library/os.html#module-os
import os
# http://docs.python.org/2.7/library/configparser.html
import ConfigParser

# http://docs.scipy.org/doc/numpy-1.6.0/reference/
import numpy as np
# http://pypi.python.org/pypi/coards/0.2.2
import coards
# http://docs.pylonsproject.org/projects/pyramid/1.0/api/response.html 
import pyramid.response 
# http://docs.pylonsproject.org/projects/pyramid/1.0/api/exceptions.html
import pyramid.exceptions
# http://docs.pylonsproject.org/projects/pyramid/1.0/api/url.html
import pyramid.url

from ccplib.datahandlers import unpack
from ccplib.visualization import spatial, temporal, ccpgraph
from ccplib.algorithms import algutils
from ccpweb import urltranslate

def get_configs(data_name, section=None):
    """
    Returns all the parameters in a given section
    Param data_name:
        The name of the data the configuration file describes
    Param section:
        The name of the section containing the requested parameters
    Return:
        If a config for data_name exists: dictionary of the parameters 
        If a config doesn't exist: a list of datasets for which configs
        exist
    """
    curdir = os.path.abspath(os.path.dirname(__file__))
    CONF_PATH = os.path.abspath(os.path.join(curdir, os.path.pardir, os.path.pardir, 'configs'))
    data_list = []
    conf_list = [os.path.join(CONF_PATH, fl) for fl in os.listdir(CONF_PATH)
                 if (os.path.splitext(fl)[-1] == '.cfg')]
    for conf in conf_list:
        #unique config object per dataset 
        config = ConfigParser.SafeConfigParser(allow_no_value=True)
        with open(conf) as confile: 
            # read for file names, readfp for file objects
            config.readfp(confile)
            conf_dname = config.get('data', 'name')
            if re.match(conf_dname, data_name, re.IGNORECASE):
                params = dict(config.items(section))
                return convert_configs(params)
            data_list.append(conf_dname)
    return dict(names=list(set(data_list)))

def convert_configs(params):
    """Does type conversion because 
    by default all configs are strings. 
    """
    # add new conversions as needed
    for k in params:
        if params[k].lower() == 'true':
            params[k] = True
        elif params[k].lower() == 'false':
            params[k] = False
        elif re.match("^[-+]?\d+$", params[k]):
            params[k] = int(params[k])
        # matches to floats and ints
        elif re.match("^[-+]?\d+.\d+$", params[k]):
            params[k] = float(params[k])
    return params

def create_data_obj(data_name):
    """ Instantiates a CCPData object using the parameters 
        in the config file and returns a ccpfig object. 
    """
    kwargs = get_configs(data_name, 'data')
    if isinstance(kwargs, list):
        raise pyramid.exceptions.NotFound()
    if kwargs:
        unpack_func = unpack.get_unpack_func(kwargs['file_type'])
        return unpack_func(**kwargs)
    return None

def select_data(data_obj, url_args):
    """Pulls out raw data based on kwargs, and passes data
       through algorithm if any are defined. 
    """
    
    data_kw = urltranslate.get_kwargs_from_url(url_args)
    data = data_obj.get_all_data(**data_kw)  
    
    # none is used as the default client side
    algkw = data_kw.get('algorithm', "none")
    
    if algkw != "none":
        algmap = algutils.dispatch()
        alg = algmap.get(algkw)
        if alg:
            data = alg(data_obj, data)
            
    return data

def objattrs(context, request):
    """Lists attributes that aren't machine specific"""
    # add keys as needed
    # rewrite this to populate metadata info box?
    attrs = ['conf_id', 'scale_factor', 'file_type', 
                'labels', 'time_units', 'add_offset', 
                'gridded', 'shape', 'missing_value', 'data_key']
                
    attrdict = dict()
    for key in attrs:
        attrdict[key] = getattr(context, key)
    
    # returns link to site serving info
    for key in ['grid', 'time']:
        attrdict[key] = pyramid.url.resource_url(context, request, 
                                              request.traversed[0], key)                                              
    return attrdict
    
def alglist():
    """Returns a list of algorithms based on what's available
       in ccplib.algorithms
    """
    alglist = ["none"]
    alglist.extend(algutils.dispatch().keys())
    return dict(names=alglist)

def valid_range(data_obj):
    """Bundles valid range attributes into a dictionary
    """
    val_range = dict()
    
    if hasattr(data_obj, 'time'):
        val_range['time'] = valid_time(data_obj.time, data_obj.time_units)
        
    if hasattr(data_obj, 'lat') and hasattr(data_obj, 'lon'):
        if data_obj.gridded:
            val_range['grid'] = valid_grid(data_obj.lat, data_obj.lon)
            
    return val_range

def valid_time(time, units):
    """Returns the first and last times in the dataset
    """
    ti = ccpgraph.timestr_ind(units)
    start = coards.from_udunits(time[0], units).isoformat()[:ti]
    end = coards.from_udunits(time[-1], units).isoformat()[:ti]
    if time[0]>time[-1]:
        start, end = end, start
    return dict(start=start.lstrip('0'), end=end.lstrip('0'))
       
def string_diff(val1, val2, chr):
    """Calculates the difference between two floats embedded in strings
    """
    return np.abs(float(val1.strip(chr))-float(val2.strip(chr)))

def valid_grid(lat, lon):
    """Returns valid grid bounds"""
    
    grid = dict()
    
    top = lat[0]
    bottom = lat[-1]
    if isinstance(top, str):
        if ('S' in top) and ('N' in bottom):
            top, bottom = bottom, top
        lat_inc = string_diff(lat[0], lat[1], 'NS')
        # add in parsing for random string formats as needed
    else:
        if top<bottom:
            top, bottom = bottom, top
        lat_inc = np.abs(lat[0]-lat[1])
        
    grid = dict(top=str(top), bottom=str(bottom), lat_inc=str(lat_inc))
    
    left = lon[0]
    right = lon[-1]
    # data files should never trigger this flip, but it's a corner case
    # for really badly formatted grids
    if isinstance(left, str):
        if ('E' in left) and ('W' in right):
            left, right = right, left
        lon_inc =  string_diff(lon[0], lon[1] , 'EW')   
    else:
        if left>right:
            left, right = right, left
        lon_inc = np.abs(lon[0]-lon[1])
    
    grid.update(dict(left=str(left), right=str(right), lon_inc=str(lon_inc)))
    return grid
                                                                                                 
        
def get_time(data_obj):
    """Returns the time dimension in the data, converted to isoformat
    """
    
    if hasattr(data_obj, 'time'):
        units = data_obj.time_units
        ti = ccpgraph.timestr_ind(units)
        time = [coards.from_udunits(t, units).isoformat()[:ti].lstrip('0')
                for t in data_obj.time]
        return time
    return 

def get_grid(data_obj):
    """Returns a dictionary containing either:
           1) the lat and lon of the dataset as lists
           2) one list of lat and lon pairs    
    """
    
    grid = dict(gridded=data_obj.gridded)
    if hasattr(data_obj, 'lat') and hasattr(data_obj, 'lon'):
        lonarr=data_obj.lon.tolist()
        lonarr = [str(lon) for lon in lonarr]
        latarr = data_obj.lat.tolist()       
        latarr = [str(lat) for lat in latarr]
        if data_obj.gridded:
            grid.update(dict(lat=latarr, lon=lonarr))
        else:
            grid.update(dict(latlon=zip(latarr, lonarr)))
    return grid
    
def set_graph(data_obj, lenshape):
    """Tries to automatically figure out if the graph should be
       spatial or temporal
   
    """
    
    if lenshape == 2:
        graph_attrs = get_configs(data_obj.conf_id, 'spatial_graph')
        graph_obj = spatial.SpatialGraph(data_obj, **graph_attrs)
    elif lenshape == 1:
        graph_attrs = get_configs(data_obj.conf_id, 'temporal_graph')
        graph_obj = temporal.TemporalGraph(data_obj, **graph_attrs)
    else:
        raise pyramid.exceptions.NotFound()
    return graph_obj
    
def drawgraph(graph_obj, im, url_args):
    """Generates the graph and writes it to the string buffer. 
    """
    
    # get kwargs for the graph:
    graph_kw = urltranslate.get_kwargs_from_url(url_args)
    
    # time_range almost always has to be in graph_kw
    # so this may be pointless
    if 'labels' not in graph_kw:
        graph_kw['labels'] = dict()
        
    if 'time_range' in graph_kw:
        graph_kw['labels'].update(time=graph_kw['time_range'])
    
    if 'coords' in graph_kw:
        graph_kw['labels'].update(location=graph_kw['coords'])
    
    # add in if 'site'
    alg = graph_kw.get('algorithm', "none")
    if alg != "none":
       graph_kw['labels'].update(alg_name=alg)
       
    # changes the figsize for a picture that's 
    # going to have an error message
    if hasattr(graph_obj, 'missing_value'): 
        if np.equal(im, graph_obj.missing_value).all():
            graph_obj.figsize = (5,5)
            # could probably just do  
            # graph_obj.ccpshow = graph_obj.nodata
    
    
    fargs = dict(facecolor='w', edgecolor='k', linewidth=2)
    # I think it turns the buffer into an httpResponse
    response = pyramid.response.Response(content_type='image/png')
    graph_obj.ccpfig(im, response, fargs, **graph_kw)
    
    return response
    


