# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
import math
import ezdxf

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


def ucs_rotation(ucs: UCS, axis: Vector, angle: float):
    # new in ezdxf v0.11: UCS.rotate(axis, angle)
    t = Matrix44.axis_rotate(axis, math.radians(angle))
    ux, uy, uz = t.transform_vectors([ucs.ux, ucs.uy, ucs.uz])
    return UCS(origin=ucs.origin, ux=ux, uy=uy, uz=uz)


def main():
    doc = ezdxf.new('R2010', setup=True)
    blk = doc.blocks.new('CSYS')
    setup_csys(blk)
    msp = doc.modelspace()

    # The DXF attribute `rotation` rotates a block reference always around the block z-axis:
    # To rotate the block reference around the WCS x-axis,
    # you have to transform the block z-axis into the WCS x-axis:
    # rotate block axis 90 deg ccw around y-axis, by using an UCS
    ucs = ucs_rotation(UCS(), axis=Y_AXIS, angle=90)
    # transform insert location, not required for (0, 0, 0)
    insert = ucs.to_ocs((0, 0, 0))
    # rotation angle about the z-axis (= WCS x-axis)
    rotation = ucs.to_ocs_angle_deg(15)
    msp.add_blockref('CSYS', insert, dxfattribs={
        'extrusion': ucs.uz,
        'rotation': rotation,
    })

    # To rotate a block reference around the block x-axis,
    # you have to find the rotated z-axis (= extrusion vector)
    # of the rotated block reference:
    # t is a transformation matrix to rotate 15 degree around the x-axis
    t = Matrix44.axis_rotate(axis=X_AXIS, angle=math.radians(15))
    # transform block z-axis into new UCS z-axis (= extrusion vector)
    uz = Vector(t.transform(Z_AXIS))
    # create new UCS at the insertion point, because we are rotating around the x-axis,
    # ux is the same as the WCS x-axis and uz is the rotated z-axis.
    ucs = UCS(origin=(1, 2, 0), ux=X_AXIS, uz=uz)
    # transform insert location to OCS, block base_point=(0, 0, 0)
    insert = ucs.to_ocs((0, 0, 0))
    # for this case a rotation around the z-axis is not required
    rotation = 0
    msp.add_blockref('CSYS', insert, dxfattribs={
        'extrusion': ucs.uz,
        'rotation': rotation,
    })

    doc.set_modelspace_vport(5)
    doc.saveas('ocs_insert.dxf')


if __name__ == '__main__':
    main()
