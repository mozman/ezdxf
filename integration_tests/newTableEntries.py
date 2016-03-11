#!/usr/bin/env python3
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: create new drawings for all supported DXF versions and create new
# table entries - check if AutoCAD accepts the new created data structures.
# Created: 20.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.lldxf.const import versions_supported_by_new


def add_table_entries(dwg):
    dwg.layers.new('MOZMAN-LAYER')
    dwg.styles.new('MOZMAN-STY')
    dwg.linetypes.new('MOZMAN-LTY', {'pattern': [1.0, .5, -.5]})
    dwg.dimstyles.new('MOZMAN-DIMSTY')
    dwg.views.new('MOZMAN-VIEW')
    dwg.viewports.new('MOZMAN-VPORT')
    dwg.ucs.new('MOZMAN-UCS')
    dwg.appids.new('MOZMANAPP')


def make_drawing(version):
    dwg = ezdxf.new(version)
    add_table_entries(dwg)
    dwg.saveas('table_entries_%s.dxf' % version)


def main():
    for version in versions_supported_by_new:
        make_drawing(version)

if __name__ == '__main__':
    main()
