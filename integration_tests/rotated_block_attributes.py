#!/usr/bin/env python3
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: create new drawings for all supported DXF versions and create new
# rotated block references - check if AutoCAD accepts the new created data structures.
# Created: 26.04.2013
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.const import versions_supported_by_new


def create_block(dwg):
    # first create a block
    flag = dwg.blocks.new(name='FLAG')

    # add dxf entities to the block (the flag)
    # use basepoint = (x, y) to define an other basepoint than (0, 0)
    flag_symbol = [(0, 0), (0, 5), (4, 3), (0, 3)]
    flag.add_polyline2d(flag_symbol)
    flag.add_circle((0, 0), .4, dxfattribs={'color': 2})

    # define some attributes
    flag.add_attdef('NAME', (0.5, -0.5), {'height': 0.5, 'color': 3})
    flag.add_attdef('XPOS', (0.5, -1.0), {'height': 0.25, 'color': 4})
    flag.add_attdef('YPOS', (0.5, -1.5), {'height': 0.25, 'color': 4})


def insert_block(layout):
    point = (10, 12)
    values = {
        'NAME': "REFNAME",
        'XPOS': "x = %.3f" % point[0],
        'YPOS': "y = %.3f" % point[1]
    }
    scale = 1.75
    layout.add_auto_blockref('FLAG', point, values, dxfattribs={
        'xscale': scale,
        'yscale': scale,
        'layer': 'FLAGS',
        'rotation': -15
    })


def make_drawing(version):
    dwg = ezdxf.new(version)
    create_block(dwg)
    insert_block(dwg.modelspace())
    dwg.saveas('rotated_block_reference_%s.dxf' % version)


def main():
    for version in versions_supported_by_new:
        make_drawing(version)

if __name__ == '__main__':
    main()
