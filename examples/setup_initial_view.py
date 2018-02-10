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
    marker.add_line((-1, 0), (1, 0), dxfattribs=attribs)
    marker.add_line((0, -1), (0, 1), dxfattribs=attribs)
    marker.add_circle((0, 0), .4, dxfattribs=attribs)

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
    # delete '*Active' viewport configuration
    dwg.viewports.delete_config('*ACTIVE')
    # the available display area in AutoCAD has the virtual lower-left corner (0, 0) and the virtual upper-right corner
    # (1, 1)

    # first viewport, uses the left half of the screen
    viewport = dwg.viewports.new('*ACTIVE')
    viewport.dxf.lower_left = (0, 0)
    viewport.dxf.upper_right = (.5, 1)
    viewport.dxf.target_point = (0, 0, 0)  # target point defines the origin of the DCS, this is the default value
    viewport.dxf.center_point = (40, 30)  # move this location (in DCS) to the center of the viewport
    viewport.dxf.height = 15  # height of viewport in drawing units, this parameter works
    viewport.dxf.aspect_ratio = 1.0  # aspect ratio of viewport (x/y)

    # second viewport, uses the right half of the screen
    viewport = dwg.viewports.new('*ACTIVE')
    viewport.dxf.lower_left = (.5, 0)
    viewport.dxf.upper_right = (1, 1)
    viewport.dxf.target_point = (60, 20, 0)  # target point defines the origin of the DCS
    viewport.dxf.center_point = (0, 0)  # move this location (in DCS, model space = 60, 20) to the center of the viewport
    viewport.dxf.height = 15  # height of viewport in drawing units, this parameter works
    viewport.dxf.aspect_ratio = 2.0  # aspect ratio of viewport (x/y)


if __name__ == '__main__':
    dwg = ezdxf.new('AC1015')
    draw_raster(dwg)
    set_active_viewport(dwg)
    dwg.saveas(FILENAME)
    print("drawing '%s' created.\n" % FILENAME)
