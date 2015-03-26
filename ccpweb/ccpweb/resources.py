#!/usr/bin/env python
#
# resources.py 
#
# Hannah Aizenman, 2011-08
#
# http://www.opensource.org/licenses/bsd-license.php

"""Manages resources for pyramid traversal
https://docs.pylonsproject.org/projects/pyramid/dev/narr/traversal.html
"""

__docformat__ = "restructuredtext"

# http://docs.python.org/library/os.html
import os

# http://docs.pylonsproject.org/projects/pyramid/1.0/api/config.html
from paste.httpserver import serve
# http://docs.pylonsproject.org/projects/pyramid/1.0/api/config.html
from pyramid.config import Configurator
# http://docs.pylonsproject.org/projects/pyramid/1.0/api/response.html"""
from pyramid.response import Response
# http://docs.pylonsproject.org/projects/pyramid/1.0/api/view.html
from pyramid.view import view_config
# http://docs.pylonsproject.org/projects/pyramid/1.0/api/exceptions.html
from pyramid.exceptions import NotFound

from ccplib.datahandlers.ccpdata import CCPData
import tasks

class Root(object):
    """Base node in the web site 
    (or first page reached to do something).
    """
    def __init__(self, request):
        self.request = request
        
    def __getitem__(self, key):
        # static pages served by root (host:) like index.html
        if 'html' in key:
            return Static()
        # list of datasets and algorithms
        # could probably be combined
        if key == 'datalist':
            return DataList()
        if key == 'alglist':
            return AlgList()
        # tries to create a data object based 
        # on the key (url subpath) passed in
        data_obj = tasks.create_data_obj(key)
        if data_obj:
            data_obj.conf_id = key
            # http://docs.pylonsproject.org/projects/pyramid/1.0/narr/resources.html#location-aware
            data_obj.__name__ = ''
            # returns CCPData Object 
            return data_obj
        else:
            return NotFound()
            
# empty class, just handled root nodes in the traversal trees
# so that the objects still have a context
# can probably be fixed by someone who actually understands
# traversal
class DataList(object):
    def __getitem__(self, key):
        pass
    
class AlgList(object):
    def __getitem__(self, key):
        pass
    
class Static(object):        
    def __getitem__(self, key):
        pass