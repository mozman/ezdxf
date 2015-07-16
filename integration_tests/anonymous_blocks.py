#!/usr/bin/env python3
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: create new drawings for all supported DXF versions and create new
# anonymous blocks  - check if AutoCAD accepts the new created data structures.
# Created: 26.04.2013
# Copyright (C) 2013, Manfred Moitzi
# License: MIT License

import logging
logging.basicConfig(level='DEBUG')

import ezdxf
from ezdxf.lldxf.const import versions_supported_by_new


def make_drawing(version):
    dwg = ezdxf.new(version)
    modelspace = dwg.modelspace()
    anonymous_block = dwg.blocks.new_anonymous_block()
    points2d = [(0,0), (1,0), (1,1), (0,1), (0,0), (1,1), (.5, 1.5), (0, 1), (1,0)]
    anonymous_block.add_polyline2d(points2d)
    modelspace.add_blockref(anonymous_block.name, (0, 0))

    dwg.saveas('anonymous_blocks_%s.dxf' % version)


def main():
    for version in versions_supported_by_new:
        make_drawing(version)

if __name__ == '__main__':
    main()
