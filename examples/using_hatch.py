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
    hatch = msp.add_hatch()  # by default a SOLID fill
    hatch.set_pattern_fill('ANSI31', color=2, scale=0.01)
    with hatch.edit_boundary() as editor:
        editor.add_polyline_path([(0, 0), (0, 3), (3, 6), (6, 6), (6, 3), (3, 0)])
    dwg.saveas("hatch_pattern_fill_polyline.dxf")

def using_hatch_style():
    def place_square_1(hatch, x, y):
        def shift(point):
            return x+point[0], y+point[1]

        with hatch.edit_boundary() as editor:
            editor.add_polyline_path(map(shift, [(0, 0), (0, 8), (8, 8), (0, 8)]))
            editor.add_polyline_path(map(shift, [(2, 2), (7, 2), (7, 7), (2, 7)]))
            editor.add_polyline_path(map(shift, [(4, 4), (6, 4), (6, 6), (4, 6)]))

    def place_square_2(hatch, x, y):
        def shift(point):
            return x+point[0], y+point[1]

        with hatch.edit_boundary() as editor:
            editor.add_polyline_path(map(shift, [(0, 0), (0, 8), (8, 8), (0, 8)]))
            editor.add_polyline_path(map(shift, [(3, 1), (7, 1), (7, 5), (3, 5)]))
            editor.add_polyline_path(map(shift, [(1, 3), (5, 3), (5, 7), (1, 7)]))

    dwg = ezdxf.new("Ac1024")
    msp = dwg.modelspace()
    hatch_style_0 = msp.add_hatch(color=3, dxfattribs={'hatch_style': 0})
    hatch_style_1 = msp.add_hatch(color=3, dxfattribs={'hatch_style': 1})
    hatch_style_2 = msp.add_hatch(color=3, dxfattribs={'hatch_style': 2})
    place_square_1(hatch_style_0, 0, 0)
    place_square_1(hatch_style_1, 10, 0)
    place_square_1(hatch_style_2, 20, 0)

    hatch_style_0b = msp.add_hatch(color=7, dxfattribs={'hatch_style': 0})
    hatch_style_1b = msp.add_hatch(color=7, dxfattribs={'hatch_style': 1})
    hatch_style_2b = msp.add_hatch(color=7, dxfattribs={'hatch_style': 2})
    place_square_2(hatch_style_0b, 0, 10)
    place_square_2(hatch_style_1b, 10, 10)
    place_square_2(hatch_style_2b, 20, 10)
    dwg.saveas("hatch_styles_examples.dxf")

def using_hatch_style_with_edge_path():
    def add_edge_path(path_editor, vertices):
        path = path_editor.add_edge_path()  # create a new edge path
        first_point = next(vertices)  # store first point for closing path
        last_point = first_point
        for next_point in vertices:
            path.add_line(last_point, next_point)  # add lines to edge path
            last_point = next_point
        path.add_line(last_point, first_point)  # close path

    def place_square_1(hatch, x, y):
        def shift(point):
            return x+point[0], y+point[1]

        with hatch.edit_boundary() as editor:
            add_edge_path(editor, map(shift, [(0, 0), (0, 8), (8, 8), (0, 8)]))
            add_edge_path(editor, map(shift, [(0, 0), (0, 8), (8, 8), (0, 8)]))
            add_edge_path(editor, map(shift, [(2, 2), (7, 2), (7, 7), (2, 7)]))
            add_edge_path(editor, map(shift, [(4, 4), (6, 4), (6, 6), (4, 6)]))

    def place_square_2(hatch, x, y):
        def shift(point):
            return x+point[0], y+point[1]

        with hatch.edit_boundary() as editor:
            add_edge_path(editor, map(shift, [(0, 0), (0, 8), (8, 8), (0, 8)]))
            add_edge_path(editor, map(shift, [(3, 1), (7, 1), (7, 5), (3, 5)]))
            add_edge_path(editor, map(shift, [(1, 3), (5, 3), (5, 7), (1, 7)]))

    dwg = ezdxf.new("Ac1024")
    msp = dwg.modelspace()
    hatch_style_0 = msp.add_hatch(color=3, dxfattribs={'hatch_style': 0})
    hatch_style_1 = msp.add_hatch(color=3, dxfattribs={'hatch_style': 1})
    hatch_style_2 = msp.add_hatch(color=3, dxfattribs={'hatch_style': 2})
    place_square_1(hatch_style_0, 0, 0)
    place_square_1(hatch_style_1, 10, 0)
    place_square_1(hatch_style_2, 20, 0)

    hatch_style_0b = msp.add_hatch(color=7, dxfattribs={'hatch_style': 0})
    hatch_style_1b = msp.add_hatch(color=7, dxfattribs={'hatch_style': 1})
    hatch_style_2b = msp.add_hatch(color=7, dxfattribs={'hatch_style': 2})
    place_square_2(hatch_style_0b, 0, 10)
    place_square_2(hatch_style_1b, 10, 10)
    place_square_2(hatch_style_2b, 20, 10)
    dwg.saveas("hatch_styles_examples_with_edge_path.dxf")

create_solid_polyline_hatch()
create_pattern_fill_polyline_hatch()
using_hatch_style()
using_hatch_style_with_edge_path()
