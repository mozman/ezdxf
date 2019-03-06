# Created: 10.04.2016
# Copyright (c) 2016-2019 Manfred Moitzi
# License: MIT License
import ezdxf

dwg = ezdxf.new2('R12', setup=True)
modelspace = dwg.modelspace()
modelspace.add_circle(center=(0, 0), radius=1.5, dxfattribs={
    'layer': 'test',
    'linetype': 'DASHED',
})

filename = 'circle.dxf'
dwg.saveas(filename)
print("drawing '%s' created.\n" % filename)
