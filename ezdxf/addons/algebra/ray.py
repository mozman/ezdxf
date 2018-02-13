#!/usr/bin/env python
#coding:utf-8
# Purpose: 2d ray - copied from algebra.Ray2D to remove dependency from the
# algebra-package
# module belongs to package: dxfwrite.py
# Created: 13.03.2010
# Copyright (C) 2010, Manfred Moitzi
# License: MIT License

""" Implements a 2D-ray class - same as algebra.Ray2D, but without the
dependency from the algebra package.

A ray is an infinite line and is defined by the equation
y(x) = y0 + x * slope in a cartesian coordinate system
"""

__author__ = "mozman <mozman@gmx.at>"

import math
from ..algebra import equals_almost, normalize_angle, is_vertical_angle

__all__ = ['Ray2D', 'ParallelRaysError']

class ParallelRaysError(ArithmeticError):
    pass

HALF_PI = math.pi / 2.
THREE_PI_HALF = 1.5 * math.pi
DOUBLE_PI = math.pi * 2.

XCOORD = 0
YCOORD = 1

class Ray2D(object):
    """defines an infinite ray (line with no end points)
    treat it as IMMUTABLE - dont't change the status
    possible keyword args: slope, angle as float
    point1, point2 as 2d-tuples

    input case A: point1, point2
    ray goes through point1 and point2, vertical lines are possible
    ignores the keyword arguments slope and angle

    input case B: point1, slope
    ray goes through point1 with slope
    argument point2 have to be None
    vertical lines are not possible because slope can't be infinite.
    ignores the keyword argument angle

    input case C: point1, angle (in radian)
    argument point2 have to be None
    ray goes through point1 with the submitted angle
    vertical lines are possible
    if keyword argument slope is defined, angle will be ignored
    """

    def __init__(self, point1, point2=None, **kwargs):
        self._vertical = False
        self.places = 7
        p1x = float(point1[XCOORD])
        p1y = float(point1[YCOORD])
        if point2 is not None: # case A
            # normalize point order to assure consist signs for slopes
            # +slope goes up and -slope goes down
            self._slope = 0
            self._angle = 0
            p2x = float(point2[XCOORD])
            p2y = float(point2[YCOORD])

            if p1x > p2x :
                p1x, p2x = p2x, p1x
                p1y, p2y = p2y, p1y
            dx = p2x - p1x
            dy = p2y - p1y
            if dx == 0. : # line is vertical
                self._x = p1x
                self._set_angle(HALF_PI)
            else :
                self._set_slope(dy/dx)
        elif 'slope' in kwargs: # case B
            self._set_slope(float(kwargs['slope']))
        elif 'angle' in kwargs: # case C
            self._set_angle(normalize_angle(float(kwargs['angle'])))
            if self.is_vertical:
                self._x = p1x
        if not self.is_vertical:
            # y0 is the y-coordinate of this ray at x-coordinate == 0
            self._y0 = p1y - self.slope * p1x

    @property
    def slope(self):
        """ get slope of the ray """
        return self._slope

    def _set_slope(self, slope): # private
        self._slope = slope
        self._angle = normalize_angle(math.atan(slope))

    @property
    def angle(self):
        return self._angle

    def _set_angle(self, angle): # private
        self._angle = angle
        self._slope = math.tan(angle)
        self._vertical = is_vertical_angle(angle)

    @property
    def is_vertical(self):
        return self._vertical
    @property
    def is_horizontal(self):
        return equals_almost(self.slope, 0., self.places)

    def is_parallel(self, ray):
        """ return True if the rays are parallel, else False"""
        if self.is_vertical:
            return ray.is_vertical
        else:
            return equals_almost(self.slope, ray.slope, self.places)

    def intersect(self, other_ray):
        """ returns the intersection point (xy-tuple) of self and
        other_ray; raises ParallelRaysError, if the rays are parallel"""
        ray1 = self
        ray2 = other_ray
        if not ray1.is_parallel(ray2):
            if ray1.is_vertical:
                x = ray1._x
                y = ray2.get_y(x)
            elif ray2.is_vertical:
                x = ray2._x
                y = ray1.get_y(x)
            else :
                # calc intersection with the 'straight-line-equation'
                # based on y(x) = y0 + x*slope
                x = (ray1._y0 - ray2._y0)/(ray2.slope - ray1.slope)
                y = ray1.get_y(x)
            return (x, y)
        else:
            raise ParallelRaysError("no intersection, rays are parallel")

    def normal_through(self, point):
        """ returns a ray which is normal to self and goes through point"""
        return Ray2D(point, angle=self.angle+HALF_PI)

    def goes_through(self, point):
        """ returns True if ray goes through point, else False"""
        if self.is_vertical:
            return equals_almost(point[XCOORD], self._x, self.places)
        else :
            return equals_almost(point[YCOORD], self.get_y(point[XCOORD]),
                                 self.places)


    def get_y(self, x):
        """ get y by x, raises ArithmeticError for vertical lines"""
        if self.is_vertical:
            raise ArithmeticError
        return self._y0 + float(x) * self.slope

    def get_x(self, y):
        """ get x by y, raises ArithmeticError for horizontal lines"""
        if self.is_vertical :
            return self._x
        else :
            if self.is_horizontal:
                raise ArithmeticError
            return (float(y) - self._y0) / self.slope

    def bisectrix(self, other_ray):
        """ bisectrix between self and other_ray """
        if self.is_parallel(other_ray):
            raise ParallelRaysError
        cross_point = self.intersect(other_ray)
        alpha = (self.angle + other_ray.angle) / 2.0
        return Ray2D(cross_point, angle=alpha)
