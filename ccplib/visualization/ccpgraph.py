#!/usr/bin/env python
#
# ccpgraph.py
#
# Hannah Aizenman, 2011-08-14
#
# http://www.opensource.org/licenses/bsd-license.php

"""This modules contains functions common to spatial and temporal graphs
"""

__docformat__ = "restructuredtext"

# http://docs.python.org/2.7/library/os.html
import os
# http://docs.python.org/2.7/library/logging.html
import logging

# http://docs.scipy.org/doc/numpy-1.6.0/user/
import numpy as np
# http://matplotlib.sourceforge.net/contents.html
import matplotlib
# http://matplotlib.sourceforge.net/api/ticker_api.html
import matplotlib.ticker
# http://matplotlib.sourceforge.net/api/cm_api.html
import matplotlib.figure
# http://matplotlib.sourceforge.net/api/backend_bases_api.html
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import ccplib.misc

log = logging.getLogger(ccplib.misc.utils.LOGNAME)

class Graph(object):
    """Handles common attributes of all graphs. More of a metaclass, 
    so generally shouldn't be called directly.    
    """
    def __init__(self, CCPData, **kwargs):
        create_folder = kwargs.get('create_folder', True)
        if create_folder:
            folder_name =  self.__class__.__name__
            self.save_path = output_folder(folder_name, 
                                           CCPData.save_path, kwargs)
        self.ext = kwargs.get('ext', 'png')
        self.threshold = kwargs.get('threshold', 5)
        self.label = kwargs.get('label', True)
        self.center = kwargs.get('center', 'auto')
       
        
        if hasattr(CCPData, 'missing_value'):
            self.missing_value = CCPData.missing_value
            
        if hasattr(CCPData, 'labels'):
            self.data_labels = CCPData.labels
            
    def __repr__(self):
        return "<{0!s}({1!r})>".format(self.__class__,self.__dict__)
                            
    def ccpfig(self, im, outfile=None, figargs=dict(), **kwargs):
        """
        Creates a figure with a single image and saves it.
        :Param im:
            Numpy array of image data
        :Param outfile: 
            The filename for the image or a buffer on 
            which to print the image
            (The default is randomly generated string)
            
        :Param figargs:
            dictionary of arguments to pass to the figure
            creation routine
        All other kwargs are passed to ccpshow
    
        """
        
        if outfile is None:
            out_file = "pic{:.0f}".format(np.floor(np.nansum(im)))
        
        if isinstance(outfile, basestring):
            image_name = ".".join([outfile, self.ext])
            save_path = kwargs.get('save_path', self.save_path)
            outfile = os.path.join(save_path, image_name)
            
        fig = matplotlib.figure.Figure(self.figsize, **figargs)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(1,1,1)
        self.ccpshow(im, ax, **kwargs)
        canvas.print_figure(outfile)
        return ax
    
    def get_labels(self, graph_data, kwargs):
        """
        Extracts default labels for the graphs from the
        function, and if there are none from the graph object, 
        and otherwise tries to obtain the labels from the data
        object. 
        :Param graph_data:
            tuple map of the fields the graph object requires and the 
            fields the data provides: 
                ex: (ylabel, variable) or (cblabel, variable)
        :Param kwargs:
            Label kwargs provided to ccpshow, vary depending 
            on the graph type
            
        """
        labels = dict()
        for gkey, dkey in graph_data:
            if gkey in kwargs:
                labels[gkey] = kwargs[gkey]
            elif hasattr(self, gkey):
                labels[gkey] = getattr(self, gkey)
            elif hasattr(self, 'data_labels'):
                labels[gkey] = self.data_labels[dkey]
            else:
                labels[gkey]= dkey
                
        if 'alg_name' in kwargs:
            alg = kwargs['alg_name'][:].capitalize()
            labels['title'] = "{} of {}".format(alg, labels['title'])
        
        return labels
                                                                                                                    
    
def output_folder(folder_name, ccp_path, kwargs):
    """Creates an output folder to dump images to. 
    """
    save_path = kwargs.get('save_path', 
                           os.path.join(ccp_path, folder_name))
    overwrite = kwargs.get('overwrite', False)
    ccplib.misc.utils.create_folder(save_path, overwrite)
    return save_path
                                                                                                                                                                  
def timestr_ind(time_units):
    """Returns index to slice an isoformatted string 
    based on the frequency of the observations.
    """
    isoplace = dict(years=4,
                    months=7,
                    days=10,
                    hours=13,
                    minutes=16,
                    seconds=19,
                    time_units = -1)   
    if 'tunit' not in isoplace:
        tunit = time_units.split(" ")[0].lower()
    return isoplace[tunit]
    

def centered(im, threshold):
    """Decides whether the values are close enough that the data
    should be centered:
        :Param im:
            Data to be evaluated
        :Param thereshold:
            Threshold for deciding the ranges are close enough together.
    Rough test is whether the range (reduced to a number between 1-10) 
    is lower then the threshold.
    
    """
    imrange = np.abs(np.abs(np.min(im))- np.abs(np.max(im)))
    if not np.isfinite(imrange) or (im>=0).all():
        log.debug("imrange is nan")
        return False
    place = int(np.log10(imrange))
    log.debug("image range: {}, place: {}".format(imrange, place))
    return (imrange/(10**place))<= threshold
                                                         
    
def labelgraph(ax, labels, cb=None):
    """Labels the graph based on the values in label.
    :Param ax:
        axis being labeled
    :Param labels:
        Dictionary of labels, and all keys are optional. 
            keys are ('title', 'xlabel', 'ylabel', 'cblabel')
    :Param cb:
        axis of the colorbar

    """
    if 'title' in labels:
        ax.set_title(labels['title'])
    if 'xlabel' in labels:
        ax.set_xlabel(labels['xlabel'])
    if 'ylabel' in labels:
        ax.set_ylabel(labels['ylabel'])
    if cb:
        cb.set_label(labels['cblabel'])
        
def nodata( ax):
    """Creates error image if data is all missing values.
    """
    ax.text(0.5, 0.5, 'no values to plot', size='x-large', 
            horizontalalignment='center', verticalalignment='center',
            transform=ax.transAxes)
    ax.axis('off')
    return
