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

def knot_values(n_control_points, degree):
    """
    :param n_control_points: count of control point
    :param degree: degree of spline
    """
    nplusc = n_control_points + degree
    nplus2 = n_control_points + 2
    x = [0.0, 0.0]
    for i in range(2, nplusc+1):
        if (i > degree) and (i < nplus2):
            x.append(x[i-1] + 1.0)
        else:
            x.append(x[i-1])
    return x

def knot_values_uniform(n_control_points, degree):
    """
    :param n_control_points: count of control point
    :param degree: degree of spline
    """
    nplusc = n_control_points + degree
    x = [0.0, 0.0]
    for i in range(2, nplusc+1):
        x.append(float(i-1))
    return x

def knot_values_by_control_points(control_points, degree):
    # defpoints has to be a 1 based array
    defpoints = ['dummy'] + [safe_3D_point(p) for p in control_points]
    n = len(defpoints) - 1
    dist = [0.0]
    for i in range(2, n+1):
        x1, y1, z1 = defpoints[i-1]
        x2, y2, z2 = defpoints[i]
        d = (x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2
        dist.append(d**0.5)
    maxc = sum(dist)
    x = [0.0] * (degree+1)
    for i in range(1, n-degree+2):
        csum = sum(dist[1:i+1])
        numerator = float(i) / float(n-degree+2) * dist[i+1] + csum
        x.append(numerator/maxc * float(n-degree+2))
    x.extend([n-degree+2] * (degree-1))
    return x
