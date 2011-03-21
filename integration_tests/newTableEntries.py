#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: create new drawings for all supported DXF versions and create new
# table entries - check if AutoCAD accepts the new created data structures.
# Created: 20.03.2011
# Copyright (C) 2011, Manfred Moitzi
# License: GPLv3

import ezdxf

VERSIONS = ['AC1009', 'AC1015', 'AC1018', 'AC1021', 'AC1024']

def add_table_entries(dwg):
    dwg.layers.create('ADDING_A_NEW_LAYER')

def make_drawing(version):
    dwg = ezdxf.new(version)
    add_table_entries(dwg)
    dwg.saveas('table_entries_%s.dxf' % version)

def main():
    for version in VERSIONS:
        make_drawing(version)

if __name__=='__main__':
    main()
