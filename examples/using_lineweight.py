# Purpose: using true color and transparency
# Created: 05.09.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf

LAYER_NAME = 'Lines'
DEFAULT_LINE_WEIGHT = 7  # AutoCAD default for 7 is 0.20mm


def lines_with_lineweight(msp, x1, x2):
    for line_weight_enum in range(27):
        y = line_weight_enum * 10
        msp.add_line(
            (x1, y),
            (x2, y),
            dxfattribs={
                'layer': LAYER_NAME,
                'lineweight': line_weight_enum,
            },
        )


def lines_with_default_weight(msp, x1, x2):
    for line_weight_enum in range(27):
        y = line_weight_enum * 10
        msp.add_line(
            (x1, y),
            (x2, y),
            dxfattribs={'layer': LAYER_NAME},
        )


dwg = ezdxf.new('AC1018')
msp = dwg.modelspace()
lines_layer = dwg.layers.new(LAYER_NAME)
# set default line width as enum
lines_layer.dxf.lineweight = DEFAULT_LINE_WEIGHT

lines_with_lineweight(msp, x1=0, x2=100)
lines_with_default_weight(msp, x1=150, x2=250)

dwg.saveas("using_lineweight.dxf")
