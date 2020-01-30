from pathlib import Path
import math
import ezdxf
from ezdxf.math import UCS

DIR = Path('~/Desktop/Outbox').expanduser()

p = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 1),
    (1, 1, 1),
    (0, 1, 1),
]

doc = ezdxf.new()
msp = doc.modelspace()
block = doc.blocks.new('block_4m3')

cube = block.add_mesh()
with cube.edit_data() as mesh_data:
    mesh_data.add_face([p[0], p[1], p[2], p[3]])
    mesh_data.add_face([p[4], p[5], p[6], p[7]])
    mesh_data.add_face([p[0], p[1], p[5], p[4]])
    mesh_data.add_face([p[1], p[2], p[6], p[5]])
    mesh_data.add_face([p[3], p[2], p[6], p[7]])
    mesh_data.add_face([p[0], p[3], p[7], p[4]])
    mesh_data.optimize()


# Place untransformed cube, don't use the rotation
# attribute unless you really need it, just
# transform the UCS.
blockref = msp.add_blockref(name='block_4m3', insert=(0, 0, 0))

# First rotation about the local x-axis
ucs = UCS().rotate_local_x(angle=math.radians(45))
# same as a rotation around the WCS x-axis:
# ucs = UCS().rotate(axis=(1, 0, 0), angle=math.radians(45))

# Second rotation about the WCS z-axis
ucs = ucs.rotate(axis=(0, 0, 1), angle=math.radians(45))

# Last step transform block reference from UCS to WCS
blockref.transform_to_wcs(ucs)

doc.set_modelspace_vport(3)
doc.saveas(DIR / 'cube.dxf')
