# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.tools import standards
from ezdxf.math import Vector

doc = ezdxf.new('R2000', setup=True)
msp = doc.modelspace()

for y, ltype in enumerate(standards.linetypes()):
    msp.add_line((0, y), (20, y), dxfattribs={'linetype': ltype[0]})
doc.set_modelspace_vport(25, center=(10, 10))
doc.saveas('linetypes.dxf')

doc = ezdxf.new('R2000', setup=True)
msp = doc.modelspace()

for r, ltype in enumerate(standards.linetypes()):
    msp.add_circle((0, 0), radius=4 + r, dxfattribs={'linetype': ltype[0]})
doc.set_modelspace_vport(50)
doc.saveas('linetypes_circle.dxf')

doc = ezdxf.new('R2000', setup=True)
msp = doc.modelspace()

points = Vector.list([(0, 0), (4, 9), (6, 9), (11, 0), (16, 9)])
for y, ltype in enumerate(standards.linetypes()):
    fitpoints = [p + (0, y) for p in points]
    msp.add_spline(fitpoints, dxfattribs={'linetype': ltype[0]})
doc.set_modelspace_vport(35, center=(8, 12))
doc.saveas('linetypes_spline.dxf')
