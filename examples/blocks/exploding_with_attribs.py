# Copyright (c) 2020, Manfred Moitzi
# License: MIT License

from typing import cast, Tuple, TYPE_CHECKING
from pathlib import Path
import ezdxf
import random

DIR = Path('~/Desktop/Outbox').expanduser()

if TYPE_CHECKING:
    from ezdxf.eztypes import Insert, BaseLayout


def get_random_point() -> Tuple[int, int]:
    """Returns random x, y coordinates."""
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return x, y


doc = ezdxf.new('R2010')
msp = doc.modelspace()

flag = doc.blocks.new(name='FLAG')
flag.add_lwpolyline([(0, 0), (0, 5), (4, 3), (0, 3)])  # the flag symbol as 2D polyline
flag.add_circle((0, 0), .4, dxfattribs={'color': 1})  # mark the base point with a circle
flag.add_attdef('NAME', (0.5, -0.5), dxfattribs={'height': 0.5, 'color': 3})
flag.add_attdef('XPOS', (0.5, -1.0), dxfattribs={'height': 0.25, 'color': 4})
flag.add_attdef('YPOS', (0.5, -1.5), dxfattribs={'height': 0.25, 'color': 4})

# Create 50 random placing points.
placing_points = [get_random_point() for _ in range(50)]

for number, point in enumerate(placing_points):
    # values is a dict with the attribute tag as item-key and
    # the attribute text content as item-value.
    values = {
        'NAME': "P(%d)" % (number + 1),
        'XPOS': "x = %.3f" % point[0],
        'YPOS': "y = %.3f" % point[1]
    }

    # Every flag has a different scaling and a rotation of +15 deg.
    random_scale = 0.5 + random.random() * 2.0
    msp.add_auto_blockref('FLAG', point, values, dxfattribs={'rotation': 15}).scale(random_scale)

doc.set_modelspace_vport(200)
doc.saveas(DIR / 'flags-with-attribs.dxf')


# Explode auto block references, wrapped into anonymous block references
for auto_blockref in msp.query("INSERT"):
    cast('Insert', auto_blockref).explode()

# Explode flag block references
for flag in msp.query("INSERT[name=='FLAG']"):
    cast('Insert', flag).explode()

doc.saveas(DIR / 'flags-exploded.dxf')
