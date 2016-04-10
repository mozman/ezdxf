#!/usr/bin/env python
#coding:utf-8
# Author:  mozman
# Purpose: ELLIPSE example
# Created: 10.04.2016
# Copyright (C) 2016 Manfred Moitzi
# License: MIT License

import ezdxf

dwg = ezdxf.new('R12')
modelspace = dwg.modelspace()
modelspace.add_circle(center=(0, 0), radius=1.5, dxfattribs={
    'layer': 'test',
    'linetype': 'DASHED',
})

filename = 'circle_R12.dxf'
dwg.saveas(filename)
print("drawing '%s' created.\n" % filename)
