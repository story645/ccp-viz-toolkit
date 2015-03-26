#!/usr/bin/env python
#
# statistics.py
#
# Hannah Aizenman, 2011-08-11

"""Thin wrapper around existing statistical functions"""

__docformat__ = "restructuredtext"

# http://docs.scipy.org/doc/numpy-1.6.0/reference/
import numpy as np

def std(DataObj, data, axis=0):
	"""Calculates the standard deviation of 
	the data, using masked arrays if needed.
	:param data:
		Numpy array of values
	:param axis:
		Axis to calculate std of.
	:return:
		Standard deviation of data
	"""
	if hasattr(DataObj, 'missing_value'):
		data = np.ma.masked_equal(data, DataObj.missing_value)
	return data.std(axis)

def mean(DataObj, data, axis=0):
	"""Calculates the standard deviation of
	the data, using masked arrays if needed.
	:param data:
		Numpy array of values
	:param axis:
		Axis to calculate on
	:return:
		Mean of the data
	"""									
	if hasattr(DataObj, 'missing_value'):
		data = np.ma.masked_equal(data, DataObj.missing_value)
	return data.mean(axis)
	