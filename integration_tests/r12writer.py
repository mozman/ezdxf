#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: test writing r12writer - reading ezdxf
# Created: 31.04.2016
# Copyright (C) 2016, Manfred Moitzi
# License: MIT License
from random import random
from ezdxf.r12writer import r12writer

FILE = "r12writer.dxf"
MAX_X_COORD = 1000.0
MAX_Y_COORD = 1000.0
CIRCLE_COUNT = 999

print("-"*20)
with r12writer(FILE) as dxf:
    dxf.add_line((0, 0), (17, 23))
    dxf.add_arc((0, 0), radius=3, start=0, end=175)
    dxf.add_solid([(0, 0), (1, 0), (0, 1), (1, 1)])
    dxf.add_point((1.5, 1.5))
    dxf.add_polyline([(5, 5), (7, 3), (7, 6)])  # 2d polyline
    dxf.add_polyline([(4, 3, 2), (8, 5, 0), (2, 4, 9)])  # 3d polyline
    dxf.add_text("test the text entity", align="MIDDLE_CENTER")

    for i in range(CIRCLE_COUNT):
        dxf.add_circle((MAX_X_COORD*random(), MAX_Y_COORD*random()), radius=2)
    print("r12writer writes {} circles.".format(CIRCLE_COUNT))

import ezdxf

dwg = ezdxf.readfile(FILE)
msp = dwg.modelspace()

circles = msp.query('CIRCLE')
print("ezdxf reads {} circles.".format(len(circles)))
if len(circles) == CIRCLE_COUNT:
    print("Test OK.")
else:
    print("Test FAILD.")
print("-"*20)
