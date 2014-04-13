# encoding: utf-8
# Purpose: 
# Created: 12.08.13
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

from .c23 import isstring

def safe_3D_point(coords):
    """Returns a 3-tuple for sure. Raises *ValueError* for axis count != (2, 3).
    """
    if isstring(coords):
        raise TypeError("string")
    coords = tuple(coords)
    if len(coords) == 3:
        return coords
    if len(coords) == 2:
        return coords[0], coords[1], 0.
    raise ValueError("Invalid axis count: {}".format(len(coords)))
