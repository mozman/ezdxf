#!/usr/bin/env python3
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: create new drawings for all supported DXF versions and create new
# graphic entities  - check if AutoCAD accepts the new created data structures.
# Created: 01.05.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import itests
import ezdxf

VERSIONS = ['AC1009', 'AC1015', 'AC1018', 'AC1021', 'AC1024']

def add_polyline2d_entities(entityspace, points):
    entityspace.add_polyline2d(points)

def add_polyline3d_entities(entityspace, points):
    entityspace.add_polyline3d(points)

def make_drawing(version):
    dwg = ezdxf.new(version)
    points2d = [(0,0), (1,0), (1,1), (0,1), (0,0), (1,1), (.5, 1.5), (0, 1), (1,0)]
    add_polyline2d_entities(dwg.modelspace(), points2d)
    points3d = [(3, 3, 0), (6, 3, 1), (6, 6, 2), (3, 6, 3), (3, 3, 4)]
    add_polyline3d_entities(dwg.modelspace(), points3d)
    dwg.saveas('polylines_%s.dxf' % version)

def main():
    for version in VERSIONS:
        make_drawing(version)

if __name__=='__main__':
    main()
