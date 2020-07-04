from pathlib import Path
import ezdxf
import math

DIR = Path('~/Desktop/Outbox').expanduser()

doc = ezdxf.new()
msp = doc.modelspace()

hatch = msp.add_hatch(color=1)
ep = hatch.paths.add_edge_path()
ep.add_line((0, 0), (1, 0))
ep.add_arc(
    center=(0, 0),
    radius=1,
    start_angle=0,
    end_angle=90,
    ccw=True,
)
ep.add_line((0, 1), (0, 0))
hatch.translate(0.25, 0.25, 0)

for color in range(2, 5):
    hatch = hatch.copy()
    hatch.dxf.color = color
    hatch.rotate_z(math.pi / 2.0)
    doc.entitydb.add(hatch)
    msp.add_entity(hatch)

doc.set_modelspace_vport(height=5)
doc.saveas(DIR / 'ccw_arc_hatch.dxf')
