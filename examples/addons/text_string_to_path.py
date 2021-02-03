#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
#
# Requires: matplotlib

from pathlib import Path
import ezdxf
from ezdxf.tools import fonts
from ezdxf.addons import text2path

DIR = Path('~/Desktop/Outbox').expanduser()
fonts.load()

doc = ezdxf.new()
doc.layers.new('OUTLINE')
doc.layers.new('FILLING')
msp = doc.modelspace()

attr = {'layer': 'OUTLINE', 'color': 1}
ff = fonts.FontFace(family="Noto Sans SC")
s = "Noto Sans SC 0123456789 %@ 中国文字"
align = "LEFT"
segments = 8

for path in text2path.make_paths_from_str(
        s, ff, align=align):
    # The font geometry consist of many small quadratic bezier curves.
    # The distance argument for the flattening method has no big impact, but
    # the segments argument is very important, which defines the minimum count
    # of approximation lines for a single curve segment.
    # The default value is 16 which is much to much for these
    # short curve segments.
    # LWPOLYLINE: this works because I know the paths are in the xy-plane,
    # else an OCS transformation would be required or use add_polyline3d().
    msp.add_lwpolyline(path.flattening(1, segments=segments), dxfattribs=attr)

attr['layer'] = 'FILLING'
attr['color'] = 2
for hatch in text2path.make_hatches_from_str(
        s, ff, align=align, dxfattribs=attr, segments=segments):
    msp.add_entity(hatch)

doc.set_modelspace_vport(10, (7, 0))
doc.saveas(DIR / 'text2path.dxf')
