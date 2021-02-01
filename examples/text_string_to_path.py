#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.render.path import from_matplotlib_path
from ezdxf.render.nesting import fast_bbox_detection

from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

DIR = Path('~/Desktop/Outbox').expanduser()

mpath = TextPath((0, 0), "matplotlib rules!", size=1,
                 prop=FontProperties(family="Arial"), usetex=False)

doc = ezdxf.new()
msp = doc.modelspace()

doc.layers.new('OUTLINE')
attr = {'layer': 'OUTLINE', 'color': 1}
for path in from_matplotlib_path(mpath):
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
for paths in fast_bbox_detection(from_matplotlib_path(mpath)):
    hatch = msp.add_hatch(color=2, dxfattribs=attr)
    ext = paths[0]
    hatch.paths.add_polyline_path(ext.flattening(1, segments=4),
                                  flags=1)  # 1=external
    if len(paths) > 1:
        for hole in paths[1]:
            hatch.paths.add_polyline_path(
                hole.flattening(1, segments=4), flags=0)  # 0=normal

doc.set_modelspace_vport(4, (3.5, 0))
doc.saveas(DIR / 'matplotlib.dxf')