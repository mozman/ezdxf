from pathlib import Path
import ezdxf
from ezdxf.addons import text2path
from ezdxf.math import Vec3
from ezdxf import path


def add_rect(p1, p2, height):
    p2 = Vec3(p2) + (0, height)
    points = [p1, (p2.x, p1.y), p2, (p1.x, p2.y)]
    msp.add_lwpolyline(points, close=True, dxfattribs={'color': 6})


DIR = Path('~/Desktop/Outbox').expanduser()
doc = ezdxf.new(setup=['styles'])
doc.styles.new('NARROW', dxfattribs={'font': 'arialn.ttf'})
msp = doc.modelspace()

p1 = Vec3(0, 0)
p2 = Vec3(12, 0)
height = 1
text = msp.add_text("Arial Narrow", dxfattribs={
    'style': 'NARROW',
    'layer': 'TEXT',
    'height': height,
    'color': 1,
})
text.set_pos(p1, p2, "LEFT")
attr = {'layer': 'OUTLINE', 'color': 2}
path.render_splines_and_polylines(
    msp, text2path.make_paths_from_entity(text), dxfattribs=attr)

p1 = Vec3(0, 2)
p2 = Vec3(12, 2)
height = 2
text = msp.add_text("OpenSansCondensed-Light", dxfattribs={
    'style': 'OpenSansCondensed-Light',
    'layer': 'TEXT',
    'height': height,
    'color': 1,
})
text.set_pos(p1, p2, "LEFT")
path.render_splines_and_polylines(
    msp, text2path.make_paths_from_entity(text), dxfattribs=attr)


doc.set_modelspace_vport(10, (6, 2))
doc.saveas(DIR / 'condensed_fonts.dxf')
