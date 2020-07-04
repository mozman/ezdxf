from pathlib import Path
import math
import ezdxf

DIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new()
msp = doc.modelspace()

# The DXF format stores the clockwise oriented start- and end angles
# for HATCH arc- and ellipse edges as complementary angle (360-angle).
# This is a problem in many ways for processing clockwise oriented
# angles correct, especially rotation transformation won't work.
# Solution: convert clockwise angles into counter-clockwise angles
# and swap start- and end angle at loading and exporting:

hatch = msp.add_hatch(color=1)
ep = hatch.paths.add_edge_path()
ep.add_line((0, 0), (0, 0.5))
ep.add_ellipse(
    center=(0, 0),
    major_axis=(1, 0),
    ratio=0.5,
    # convert and swap start- and end angles
    start_angle=0,  # DXF: 270 = 360 - 90
    end_angle=90,  # DXF: 360 = 360 - 0
    ccw=False,
)
ep.add_line((1, 0), (0, 0))
hatch.translate(0.25, 0.25, 0)
hatches = [hatch]

# By converting and swapping start- and end angles, transformation works:
for color in range(2, 5):
    hatch = hatch.copy()
    hatch.dxf.color = color
    hatch.rotate_z(math.pi / 2.0)
    doc.entitydb.add(hatch)
    msp.add_entity(hatch)
    hatches.append(hatch)


def transform(e):
    e.rotate_x(math.pi/4)
    e.rotate_y(math.pi/4)


lines = []
for hatch in hatches:
    for edge in hatch.paths[0]:
        if edge.EDGE_TYPE == 'LineEdge':
            lines.append(msp.add_line(edge.start, edge.end, dxfattribs={'color': 6}))

for hatch in hatches:
    transform(hatch)

for line in lines:
    transform(line)

doc.set_modelspace_vport(height=5)
doc.saveas(DIR / 'cw_ellipse_hatch_3d.dxf')
