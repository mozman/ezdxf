#!/usr/bin/env python
#coding:utf-8
# Author:  mozman -- <mozman@gmx.at>
# Purpose: using hatch
# Created: 21.06.2015
# Copyright (C) , Manfred Moitzi
# License: MIT License

import ezdxf


def create_solid_polyline_hatch():
    dwg = ezdxf.new("Ac1024")
    msp = dwg.modelspace()
    hatch = msp.add_hatch(color=2)  # by default a SOLID fill
    with hatch.edit_boundary() as editor:
        editor.add_polyline_path([(0, 0), (0, 3), (3, 6), (6, 6), (6, 3), (3, 0)])
    dwg.saveas("hatch_solid_polyline.dxf")

def create_pattern_fill_polyline_hatch():
    dwg = ezdxf.new("Ac1024")
    msp = dwg.modelspace()
    hatch = msp.add_hatch() # by default a SOLID fill
    hatch.set_pattern_fill('ANSI31', 2, scale=0.01)
    with hatch.edit_boundary() as editor:
        editor.add_polyline_path([(0, 0), (0, 3), (3, 6), (6, 6), (6, 3), (3, 0)])
    dwg.saveas("hatch_pattern_fill_polyline.dxf")


create_solid_polyline_hatch()
create_pattern_fill_polyline_hatch()
