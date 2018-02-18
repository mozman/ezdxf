# Purpose: ELLIPSE example
# Created: 10.04.2016
# Copyright (c) 2016 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf

dwg = ezdxf.new('AC1015')
modelspace = dwg.modelspace()
modelspace.add_ellipse(center=(0, 0), major_axis=(3, 1), ratio=0.65, dxfattribs={
    'layer': 'test',
    'linetype': 'DASHED',
})

filename = 'ellipse.dxf'
dwg.saveas(filename)
print("drawing '%s' created.\n" % filename)
