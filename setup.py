# http://docs.python.org/2.7/library/os.html                                              
import os                                                                                 
# http://docs.python.org/2.7/distutils/setupscript.html                                   
from distutils.core import setup                                                          
                                                                                          
# rewrite packages to be more flexible                                                    
# this is ugly but finds all the subpackages                                              
# as I couldn't find a function for this in disutils                                      
                                                                                          
name = 'ccplib'                                                                           
contents = [os.path.join(name, fl) for fl in os.listdir(name)]                            
packages = ['ccplib'].extend([c for c in contents if os.path.isdir(c)])#!/usr/bin/bash python

"""This file just installs ccplib.
"""

# http://docs.python.org/2.7/library/os.html
import os
# http://docs.python.org/2.7/distutils/setupscript.html
from distutils.core import setup

# rewrite packages to be more flexible
# this is ugly but finds all the subpackages
# as I couldn't find a function for this in disutils

name = 'ccplib'
contents = [os.path.join(name, fl) for fl in os.listdir(name)]
packages = ['ccplib'].extend([c for c in contents if os.path.isdir(c)])        


setup(name = name,
      version = "0.1",
      description = "Common Climate Project visualization toolkit",
      packages = packages,
      author = "hannah",
      author_email = "haizenm00@ccny.cuny.edu")