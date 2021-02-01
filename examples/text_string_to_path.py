#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.render.path import from_matplotlib_path

from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

DIR = Path('~/Desktop/Outbox').expanduser()

mpath = TextPath((0, 0), "matplotlib rules!", size=1,
                 prop=FontProperties(family="Arial"), usetex=False)

doc = ezdxf.new()
msp = doc.modelspace()
for path in from_matplotlib_path(mpath):
    # The font geometry consist of many small quadratic bezier curves.
    # The distance argument for the flattening method has no big impact, but
    # the segments argument is very important, which defines the minimum count
    # of approximation lines for a single curve segment.
    # The default value is 16 which is much to much for these
    # short curve segments:
    msp.add_lwpolyline(path.flattening(1, segments=4))
doc.set_modelspace_vport(4, (3.5, 0))
doc.saveas(DIR / 'matplotlib.dxf')