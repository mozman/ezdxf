# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import ezdxf
from ezdxf.tools import standards


doc = ezdxf.new('R2000', setup=True)
msp = doc.modelspace()

for y, ltype in enumerate(standards.linetypes()):
    msp.add_line((0, y), (20, y), dxfattribs={'linetype': ltype[0]})
doc.saveas('linetypes.dxf')
