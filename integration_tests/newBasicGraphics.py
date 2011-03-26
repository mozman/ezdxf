#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: create new drawings for all supported DXF versions and create new
# graphic entities  - check if AutoCAD accepts the new created data structures.
# Created: 25.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import ezdxf

VERSIONS = ['AC1009', 'AC1015', 'AC1018', 'AC1021', 'AC1024']

def add_line_entities(workspace, offset):
    for color in range(1, 256):
        line = workspace.add_line((offset+0, color), (offset+50, color), {'color': color})

def make_drawing(version):
    dwg = ezdxf.new(version)
    add_line_entities(dwg.modelspace(), 0)
    add_line_entities(dwg.paperspace(), 70)
    dwg.saveas('basic_graphics_%s.dxf' % version)

def main():
    for version in VERSIONS:
        make_drawing(version)

if __name__=='__main__':
    main()
