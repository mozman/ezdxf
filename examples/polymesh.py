#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: example for polymesh usage
# Created: 31.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import sys
import os
import math

import ezdxf
MSIZE = 20
HEIGHT = 3.

def build_mesh(polymesh):
    msize = polymesh.mcount
    nsize = polymesh.ncount
    mdelta = math.pi / msize
    ndelta = math.pi / nsize

    for x in range(msize):
        sinx = math.sin(float(x)*mdelta)
        for y in range(nsize):
            cosy = math.cos(float(y)*ndelta)
            z = sinx * cosy * HEIGHT
            # set the m,n vertex to 3d point x,y,z
            polymesh.set_mesh_vertex(pos=(x, y), point=(x, y, z))

dwg = ezdxf.new('AC1009') # DXF R12
layout = dwg.modelspace()
polymesh = layout.add_polymesh(size=(MSIZE, MSIZE))
build_mesh(polymesh)

filename='polymesh.dxf'
dwg.saveas(filename)
print("drawing '%s' created.\n" % filename)
