#!/usr/bin/env python3
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: create new drawings for all supported DXF versions and create new
# table entries - check if AutoCAD accepts the new created data structures.
# Created: 20.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: MIT License

import itests
import ezdxf

VERSIONS = ['AC1009', 'AC1015', 'AC1018', 'AC1021', 'AC1024']

def add_table_entries(dwg):
    dwg.layers.create('MOZMAN-LAYER')
    dwg.styles.create('MOZMAN-STY')
    dwg.linetypes.create('MOZMAN-LTY', {'pattern': [1.0, .5, -.5]})
    dwg.dimstyles.create('MOZMAN-DIMSTY')
    dwg.views.create('MOZMAN-VIEW')
    dwg.viewports.create('MOZMAN-VPORT')
    dwg.ucs.create('MOZMAN-UCS')
    dwg.appids.create('MOZMANAPP')

def make_drawing(version):
    dwg = ezdxf.new(version)
    add_table_entries(dwg)
    dwg.saveas('table_entries_%s.dxf' % version)

def main():
    for version in VERSIONS:
        make_drawing(version)

if __name__=='__main__':
    main()
