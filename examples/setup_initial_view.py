#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: setup initial viewport for a DXF drawing
# Copyright (C) 2016-2018 Manfred Moitzi
# License: MIT License

import ezdxf
FILENAME = r'C:\Users\manfred\Desktop\Now\setup_initial_view.dxf'


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


def setup_active_viewport(dwg):
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


def setup_paper_space_layout(dwg, name):
    if name in dwg.layouts:
        layout = dwg.layouts.get(name)
    else:
        layout = dwg.layouts.new(name)
    layout.paper_setup(size=(11, 8.5), margins=(.5, .5, .5, .5), units='inch')
    layout.add_line((-0.5, 3.75), (10.5, 3.75))  # hor center line
    layout.add_line((5., -0.5), (5., 8.0))  # vert center line
    layout2 = dwg.layouts.new('mozman 1_1')
    layout2.paper_setup(size=(297, 210), margins=(10, 10, 10, 10), units='mm')
    layout2.add_viewport(
        center=(100, 100),  # center of viewport in paper_space units
        size=(50, 50),  # viewport size in paper_space units
        view_center_point=(60, 40),  # model space point to show in center of viewport in WCS
        view_height=20,  # how much model space area to show in viewport in drawing units
    )
    layout2.add_line((0, 100), (200, 100))  # hor center line
    layout2.add_line((150, 0), (150, 150))  # vert center line

    layout3 = dwg.layouts.new('mozman 1_50')
    layout3.paper_setup(size=(297, 210), margins=(10, 10, 10, 10), units='mm', scale=(1, 50))
    layout3.add_viewport(
        center=(5000, 5000),  # center of viewport in paper_space units, scale = 1:50
        size=(5000, 2500),  # viewport size in paper_space units, scale = 1:50
        view_center_point=(60, 40),  # model space point to show in center of viewport in WCS
        view_height=20,  # how much model space area to show in viewport in drawing units
    )


if __name__ == '__main__':
    dwg = ezdxf.new('AC1015')
    draw_raster(dwg)
    setup_active_viewport(dwg)
    setup_paper_space_layout(dwg, 'Layout1')
    dwg.saveas(FILENAME)
    print("drawing '%s' created.\n" % FILENAME)
