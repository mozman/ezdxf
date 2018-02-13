#!/usr/bin/env python
#coding:utf-8
# Purpose: 2d clothoid
# module belongs to package: dxfwrite.py
# Created: 26.03.2010
# License: MIT License

__author__ = "mozman <mozman@gmx.at>"

import sys
if sys.version_info[0] > 2:
    xrange = range

import math

class Clothoid(object):
    """This object represents a clothoid (a.k.a. Euler spiral) for parameter
    <paramA>. The curve always starts at the coordinate system origin = (0, 0).
    """
    def __init__(self, paramA=1.0):
        self.A = paramA # Clothiod Parameter A
        self.powersA = [paramA**power for power in xrange(19)]
        self.coords = {} # coordinates cache

    def get_radius(self, L):
        """Get radius of circle at distance <L>."""
        if L > 0.:
            return self.powersA[2] / L
        else :
            return 0. # radius = infinite

    def get_tau(self, L):
        """Get tangent angle at distance <L> in radians."""
        return L**2 / (2. * self.powersA[2])

    def get_L(self, radius):
        """Get distance L from origin for <radius>."""
        return self.powersA[2] / float(radius)

    def get_xy(self, L):
        """Get xy-coordinates of curve point at distance <L>."""
        def term(powerL, powerA, const):
            return L**powerL/(const * self.powersA[powerA])
        if L not in self.coords:
            y = term(3, 2, 6.) - term(7, 6, 336.) + term(11, 10, 42240.) - \
                term(15, 14, 9676800.) + term(19, 18, 3530096640.)
            x = L - term(5, 4, 40.) + term(9, 8, 3456.) - term(13, 12, 599040.) + \
                term(17, 16, 175472640.)
            self.coords[L] = (x, y)
        return self.coords[L]

    def approximate(self, length, segments):
        """Approximate curve of <length> with <segments> line-segments.

        Generates <segments>+1 2D points (float, float).
        """
        delta_l = float(length) / float(segments)
        yield (0., 0.)
        for index in xrange(1, segments+1):
            yield self.get_xy(delta_l * index)

    def get_center(self, L):
        """Get center point of circle at point L."""
        x, y = self.get_xy(L)
        r = self.get_radius(L)
        tau = self.get_tau(L)
        xm = x - r * math.sin(tau)
        ym = y + r * math.cos(tau)
        return (xm, ym)
