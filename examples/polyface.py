#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: examples for dxfwrite usage, see also tests for examples
# Created: 09.02.2010
# Copyright (C) 2010, Manfred Moitzi
# License: MIT License

import sys
import os

from random import random

import ezdxf

def build_cube(layout, basepoint, length):
    def scale( point ):
        return ( (basepoint[0]+point[0]*length),
                 (basepoint[1]+point[1]*length),
                 (basepoint[2]+point[2]*length))

    # cube corner points
    p1 = scale( (0,0,0) )
    p2 = scale( (0,0,1) )
    p3 = scale( (0,1,0) )
    p4 = scale( (0,1,1) )
    p5 = scale( (1,0,0) )
    p6 = scale( (1,0,1) )
    p7 = scale( (1,1,0) )
    p8 = scale( (1,1,1) )

    # define the 6 cube faces
    # look into -x direction
    # Every add_face adds 4 vertices 6x4 = 24 vertices
    pface = layout.add_polyface()
    pface.append_face([p1, p5, p7, p3], {'color': 1}) # base
    pface.append_face([p1, p5, p6, p2], {'color': 2}) # left
    pface.append_face([p5, p7, p8, p6], {'color': 3}) # front
    pface.append_face([p7, p8, p4, p3], {'color': 4}) # right
    pface.append_face([p1, p3, p4, p2], {'color': 5}) # back
    pface.append_face([p2, p6, p8, p4], {'color': 6}) # top

def build_all_cubes(layout):
    #build_cube(layout, basepoint=(0, 0, 0), length=1)
    #return
    for x in range(10):
        for y in range(10):
            build_cube(layout, basepoint=(x,y, random()), length=random())

dwg = ezdxf.new('AC1009') # DXF R12
layout = dwg.modelspace()
build_all_cubes(layout)

filename='polyface.dxf'
dwg.saveas(filename)
print("drawing '%s' created.\n" % filename)
