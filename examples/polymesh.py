#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: example for polymesh usage
# Created: 31.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

import sys
import os
import math

import ezdxf
MSIZE = 20
HEIGHT = 3.

def build_mesh(polymesh):
    m_size = polymesh.dxf.m_count
    n_size = polymesh.dxf.n_count
    m_delta = math.pi / m_size
    n_delta = math.pi / n_size

    for x in range(m_size):
        sinx = math.sin(float(x)*m_delta)
        for y in range(n_size):
            cosy = math.cos(float(y)*n_delta)
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
