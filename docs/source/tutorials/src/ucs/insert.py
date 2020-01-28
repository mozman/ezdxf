# Copyright (c) 2020 Manfred Moitzi
# License: MIT License
import math, sys
import ezdxf
from pathlib import Path

OUT_DIR = Path('~/Desktop/Outbox').expanduser()

from ezdxf.lldxf.const import MIRROR_X
from ezdxf.math import UCS, Vector, Matrix44, Y_AXIS, X_AXIS, Z_AXIS

RED = 1
GREEN = 3
BLUE = 5


def setup_csys(blk, size=3):
    # draw axis
    blk.add_line((0, 0), (size, 0), dxfattribs={'color': RED})  # x-axis
    blk.add_line((0, 0), (0, size), dxfattribs={'color': GREEN})  # y-axis
    blk.add_line((0, 0), (0, 0, size), dxfattribs={'color': BLUE})  # z-axis

    # place text
    size2 = size / 2
    txt_props = {
        'style': 'OpenSans',
        'height': size / 2,
        'color': RED,
    }
    # XY-plane text
    blk.add_text('XY', dxfattribs=txt_props).set_pos((size2, size2), align='MIDDLE_CENTER')

    # YZ-plane text
    ucs = UCS(ux=(0, 1, 0), uy=(0, 0, 1))
    txt_props['extrusion'] = ucs.uz
    txt_props['color'] = GREEN
    blk.add_text('YZ', dxfattribs=txt_props).set_pos(ucs.to_ocs((size2, size2)), align='MIDDLE_CENTER')

    # XZ-plane text
    ucs = UCS(ux=(1, 0, 0), uy=(0, 0, 1))
    txt_props['extrusion'] = ucs.uz
    txt_props['color'] = BLUE
    txt_props['text_generation_flag'] = MIRROR_X
    blk.add_text('XZ', dxfattribs=txt_props).set_pos(ucs.to_ocs((size2, size2)), align='MIDDLE_CENTER')


doc = ezdxf.new('R2010', setup=True)
blk = doc.blocks.new('CSYS')
setup_csys(blk)
msp = doc.modelspace()

ucs = UCS().rotate_local_y(angle=math.radians(90))
msp.add_blockref(
    'CSYS',
    insert=(0, 0),
    # rotation around the block z-axis (= WCS x-axis)
    dxfattribs={'rotation': 15},
).transform_to_wcs(ucs)

doc.set_modelspace_vport(5)
doc.saveas(OUT_DIR / 'ucs_insert_01.dxf')
msp.delete_all_entities()

# Rotating a block reference around the block x-axis,
# by rotating the UCS:
ucs = UCS(origin=(1, 2, 0)).rotate_local_x(math.radians(15))
blockref = msp.add_blockref('CSYS', insert=(0, 0, 0))
blockref.transform_to_wcs(ucs)

doc.saveas(OUT_DIR / 'ucs_insert_02.dxf')

# New UCS at the translated location, axis aligned to the WCS
ucs = UCS((-3, -1, 1))
# Transform an already placed block reference, including
# the transformation of the established OCS.
blockref.transform_to_wcs(ucs)

doc.saveas(OUT_DIR / 'ucs_insert_03.dxf')

# Rotate a block references with an established OCS around the
# block y-axis about 90 degree
# Get UCS at the block reference insert location, UCS axis aligned
# to the block axis.
ucs = blockref.ucs()
# Rotate UCS around the local y-axis.
ucs = ucs.rotate_local_y(math.radians(-90))

# Reset block reference parameters to place block reference in
# UCS origin, without any rotation and OCS.
blockref.reset_transformation()

# Transform block reference from UCS to WCS
blockref.transform_to_wcs(ucs)

doc.saveas(OUT_DIR / 'ucs_insert_04.dxf')
