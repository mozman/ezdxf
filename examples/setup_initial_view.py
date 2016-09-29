#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: setup initial viewport for a DXF drawing
# Created: 26.09.2016
# Copyright (C) 2016 Manfred Moitzi
# License: MIT License

import ezdxf
FILENAME = 'setup_initial_view.dxf'


def draw_raster(dwg):
    marker = dwg.blocks.new(name='MARKER')
    attribs = {'color': 2}
    marker.add_line((-1, 0), (1, 0), dxfattribs=attribs.copy())
    marker.add_line((0, -1), (0, 1), dxfattribs=attribs.copy())
    marker.add_circle((0, 0), .4, dxfattribs=attribs.copy())

    marker.add_attdef('XPOS', (0.5, -1.0), dxfattribs={'height': 0.25, 'color': 4})
    marker.add_attdef('YPOS', (0.5, -1.5), dxfattribs={'height': 0.25, 'color': 4})
    modelspace = dwg.modelspace()
    for x in range(10):
        for y in range(10):
            xcoord = x * 10
            ycoord = y * 10
            values = {
                'XPOS': "x = %d" % xcoord,
                'YPOS': "y = %d" % ycoord
            }
            modelspace.add_auto_blockref('MARKER', (xcoord, ycoord), values)


def set_active_viewport(dwg):
    try:
        active_viewport = dwg.viewports.get('*ACTIVE')
    except ValueError:
        active_viewport = dwg.viewports.new('*ACTIVE')
    # first try, the logic way - but wrong!
    # active_viewport.dxf.lower_left = (20, 20)
    # active_viewport.dxf.upper_right = (40, 30)
    # second try
    active_viewport.dxf.center_point = (40, 30)  # center of viewport, this parameter works
    active_viewport.dxf.height = 15  # height of viewport, this parameter works
    active_viewport.dxf.aspect_ratio = 1.5  # aspect ratio of viewport (x/y)


if __name__ == '__main__':
    dwg = ezdxf.new('AC1015')
    draw_raster(dwg)
    set_active_viewport(dwg)
    dwg.saveas(FILENAME)
    print("drawing '%s' created.\n" % FILENAME)
