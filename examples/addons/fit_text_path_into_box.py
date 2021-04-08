#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf import path, zoom
from ezdxf.math import Matrix44
from ezdxf.tools import fonts
from ezdxf.addons import text2path

DIR = Path('~/Desktop/Outbox').expanduser()
fonts.load()

doc = ezdxf.new()
doc.layers.new('OUTLINE')
doc.layers.new('FILLING')
msp = doc.modelspace()

attr = {'layer': 'OUTLINE', 'color': 1}
ff = fonts.FontFace(family="Arial")
sx, sy = 4, 2
# create target box
msp.add_lwpolyline([(0, 0), (sx, 0), (sx, sy), (0, sy)], close=True)
text_as_paths = text2path.make_paths_from_str("Squeeze Me", ff)
final_paths = path.fit_paths_into_box(text_as_paths, size=(sx, sy, 0), uniform=False)
final_paths = path.transform_paths(final_paths, Matrix44.scale(-1, 1, 1))

# move bottom/left corner to (0, 0) if required:
bbox = path.bbox(final_paths)
dx, dy, dz = -bbox.extmin
final_paths = path.transform_paths(final_paths, Matrix44.translate(dx,dy, dz))

path.render_lwpolylines(msp, final_paths, distance=0.01, dxfattribs=attr)

zoom.extents(msp)
doc.saveas(DIR / 'text2path.dxf')
