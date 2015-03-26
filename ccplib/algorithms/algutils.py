#!/usr/bin/env python
#
# algutils.py
#
# Hannah Aizenman, 2011-08-11

"""Functions for managing algorithms"""

__docformat__ = "restructuredtext"

from ccplib.algorithms import statistics

def dispatch():
    """Maps algorithm name to a function in ccplib.algorithms
    """
    algmap = dict(mean = statistics.mean,
                  std = statistics.std)
    return algmap