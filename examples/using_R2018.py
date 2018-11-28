# Purpose: circle example for DXF version AC1032/R2018
# Created: 27.12.2017
# Copyright (C) 2017 Manfred Moitzi
# License: MIT License
import ezdxf

dwg = ezdxf.new('R2018')
modelspace = dwg.modelspace()
modelspace.add_circle(center=(0, 0), radius=1.5, dxfattribs={
    'layer': 'test',
    'linetype': 'DASHED',
})

filename = 'circle_R2018.dxf'
dwg.saveas(filename)
print("drawing '%s' created.\n" % filename)
