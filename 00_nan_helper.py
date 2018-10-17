# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 14:13:48 2018

https://stackoverflow.com/questions/6518811/interpolate-nan-values-in-a-numpy-array#6520696

@author: eat
@edited: snake_charmer
"""

import numpy as np

def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
          to convert logical indices of NaNs to 'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    """

    return np.isnan(y), lambda z: z.nonzero()[0]

"""
>>> y= array([1, 1, 1, NaN, NaN, 2, 2, NaN, 0])
>>>
>>> nans, x= nan_helper(y)
>>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
>>>
>>> print y.round(2)
[ 1.    1.    1.    1.33  1.67  2.    2.    1.    0.  ]

"""
