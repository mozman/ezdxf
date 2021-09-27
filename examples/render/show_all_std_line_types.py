# Copyright (c) 2019-2021, Manfred Moitzi
# License: MIT License

import ezdxf
from ezdxf.math import Vec3
from ezdxf.tools.standards import linetypes

doc = ezdxf.new("R2007", setup=True)
msp = doc.modelspace()

# How to change the global linetype scaling:
doc.header["$LTSCALE"] = 0.5

p1 = Vec3(0, 0)
p2 = Vec3(9, 0)
delta = Vec3(0, -1)
text_offset = Vec3(0, 0.1)

for lt in linetypes():
    name = lt[0]
    msp.add_line(p1, p2, dxfattribs={"linetype": name, "lineweight": 25})
    msp.add_text(
        name, dxfattribs={"style": "OpenSansCondensed-Light", "height": 0.25}
    ).set_pos(p1 + text_offset)
    p1 += delta
    p2 += delta

doc.set_modelspace_vport(25, center=(5, -10))
doc.saveas("all_std_line_types.dxf")
