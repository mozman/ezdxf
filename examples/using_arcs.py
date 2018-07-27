# Purpose: ARC example
# Created: 09.07.2018
# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import ezdxf

dwg = ezdxf.new('R2000')
modelspace = dwg.modelspace()

delta = 30
for count in range(12):
    modelspace.add_arc(center=(0, 0), radius=10+count, start_angle=count*delta, end_angle=(count+1)*delta)

filename = 'using_arcs.dxf'
dwg.saveas(filename)
print("drawing '%s' created.\n" % filename)
