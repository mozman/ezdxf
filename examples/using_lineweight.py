# Purpose: using true color and transparency
# Created: 05.09.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
import ezdxf

LAYER_NAME = 'Lines'

# line weight im mm times 100, e.g. 0.13mm = 13
# minimum line weight 13
# maximum line width 200
WEIGHTS = [13, 18, 20, 25, 35, 50, 70, 100, 200, -1, -3]


def lines_with_lineweight(msp, x1, x2):
    for index, lineweight in enumerate(WEIGHTS):
        y = index * 10
        msp.add_line(
            (x1, y),
            (x2, y),
            dxfattribs={
                'layer': LAYER_NAME,
                'lineweight': lineweight,
            },
        )


def lines_with_default_weight(msp, x1, x2):
    for index in range(len(WEIGHTS)):
        y = index * 10
        msp.add_line(
            (x1, y),
            (x2, y),
            dxfattribs={'layer': LAYER_NAME},
        )


doc = ezdxf.new('R2004')
msp = doc.modelspace()
lines_layer = doc.layers.new(LAYER_NAME)
# set default line width as enum
lines_layer.dxf.lineweight = 35

lines_with_lineweight(msp, x1=0, x2=100)
lines_with_default_weight(msp, x1=150, x2=250)

doc.saveas("using_lineweight.dxf")
