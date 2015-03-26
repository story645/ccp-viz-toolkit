#!/usr/bin/env python
#
# views.py
#
# Hannah Aizenman, 2011-08
#
# http://www.opensource.org/licenses/bsd-license.php

"""Views (web pages) served by ccpweb.
"""

__docformat__ = "restructuredtext"

# http://docs.python.org/library/os.html
import os

# https://docs.pylonsproject.org/projects/pyramid/1.0/api/response.html
from pyramid.response import Response
# http://docs.pylonsproject.org/projects/pyramid/1.0/api/view.html
from pyramid.view import view_config
# http://docs.pylonsproject.org/projects/pyramid/1.0/api/exceptions.html
from pyramid.exceptions import NotFound

from ccplib.datahandlers.ccpdata import CCPData
from ccpweb.resources import DataList, AlgList, Static
from ccpweb import tasks

SITE_LIB_ROOT = os.path.abspath(os.path.dirname(__file__))

# ccpviz.html
@view_config(context=Static, request_method='GET')
def page_view(context, request):
    key = request.traversed[0]
    pagepath = os.path.join(SITE_LIB_ROOT, key)
    try:
        page = open(pagepath).read()
        return Response(content_type='text/html', body=page)
    except IOError, e:
        return NotFound()

# list of available datasets
@view_config(context=DataList, request_method='GET', renderer='json')
def get_datalist(context, request):
    return tasks.get_configs(" ")

# list of algorithms
@view_config(context=AlgList, request_method='GET', renderer='json')
def get_alglist(context, request):
    return tasks.alglist()

# random metadata about the dataset 
@view_config(context=CCPData, request_method='GET')
def get_objattrs(context, request):
    return Response(tasks.objattrs(context, request))

#bundles time and grid in one request/json object
@view_config(context=CCPData, name='menu', request_method='GET', renderer='json')
def get_dsmenu(context, request):
    dsmenu = dict(time=tasks.get_time(context))
    dsmenu.update(tasks.get_grid(context))
    return dsmenu

# Returns dictionary of valid ranges 
@view_config(context=CCPData, name='validrange', request_method='GET', renderer='json')
def get_valid_range(context, request):
   return tasks.valid_range(context)

# returns time as a long space seperated string so that
# it's used to populate autocomplete
@view_config(context=CCPData, name='time', request_method='GET')
def get_time(context, request):
    time = tasks.get_time(context)
    return Response("\n".join(time))
    
# bundles the lat and lon arrays/list into a json object
@view_config(context=CCPData, name='grid', request_method='GET', renderer='json')
def get_grid(context, request):
    latlon = tasks.get_grid(context)
    return latlon
    
# returns the data/doesn't quite work as expected
@view_config(context=CCPData, name='data', request_method='GET')
def get_data(context, request):  
    image = tasks.select_data(context, request.subpath)
    return Response(image)

# returns the graph as a response
@view_config(context=CCPData, name='graph', request_method='GET')
def make_graph(context, request):
    image = tasks.select_data(context, request.subpath)
    graph_obj = tasks.set_graph(context, image.ndim)
    return tasks.drawgraph(graph_obj, image, request.subpath)             

# 404 page-should be replaced with something fun
@view_config(context='pyramid.exceptions.NotFound')
def notfound_view(self):
    return Response('404: Page Not Found.')
                 
# used to test stuff/part of the paster default
def my_view(request):
    return {'project':'ccpweb'}
