#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
#
# Requires: matplotlib

from pathlib import Path
import ezdxf
from ezdxf.tools import fonts
from ezdxf.render.path import from_matplotlib_path
from ezdxf.addons import text2path

from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

DIR = Path('~/Desktop/Outbox').expanduser()
fonts.load()

mpath = TextPath((0, 0), "matplotlib 0123", size=1,
                 prop=FontProperties(family="Source Code Pro"), usetex=False)

doc = ezdxf.new()
msp = doc.modelspace()

doc.layers.new('OUTLINE')
attr = {'layer': 'OUTLINE', 'color': 1}
ff = fonts.FontFace(family="Source Code Pro")
for path in text2path.make_paths_from_str("matplotlib 0123", ff, halign=1):
    # The font geometry consist of many small quadratic bezier curves.
    # The distance argument for the flattening method has no big impact, but
    # the segments argument is very important, which defines the minimum count
    # of approximation lines for a single curve segment.
    # The default value is 16 which is much to much for these
    # short curve segments:
    msp.add_lwpolyline(path.flattening(1, segments=4), dxfattribs=attr)

# The following code will be a function in the new text2path add-on.
doc.layers.new('FILLING')
attr['layer'] = 'FILLING'
for contour, holes in text2path.group_contour_and_holes(
        from_matplotlib_path(mpath)):
    hatch = msp.add_hatch(color=2, dxfattribs=attr)
    hatch.paths.add_polyline_path(contour.flattening(1, segments=4),
                                  flags=1)  # 1=external
    for hole in holes:
        hatch.paths.add_polyline_path(
            hole.flattening(1, segments=4), flags=0)  # 0=normal

doc.set_modelspace_vport(4, (3.5, 0))
doc.saveas(DIR / 'matplotlib.dxf')
