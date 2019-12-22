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
    # msp.add_blockref('CSYS', insert, dxfattribs={
    #    'extrusion': ucs.uz,
    #    'rotation': rotation,
    # })

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
    blockref = msp.add_blockref('CSYS', insert, dxfattribs={
        'extrusion': ucs.uz,
        'rotation': rotation,
    })

    # translate a block references with an established OCS
    translation = Vector(-3, -1, 1)
    # get established OCS
    ocs = blockref.ocs()
    # get insert location in WCS
    actual_wcs_location = ocs.to_wcs(blockref.dxf.insert)
    # translate location
    new_wcs_location = actual_wcs_location + translation
    # convert WCS location to OCS location
    blockref.dxf.insert = ocs.from_wcs(new_wcs_location)

    # rotate a block references with an established OCS around the block y-axis about 90 degree
    ocs = blockref.ocs()
    # convert block y-axis (= rotation axis) into WCS vector
    rotation_axis = ocs.to_wcs((0, 1, 0))
    # convert local z-axis (=extrusion vector) into WCS vector
    local_z_axis = ocs.to_wcs((0, 0, 1))
    # build transformation matrix
    t = Matrix44.axis_rotate(axis=rotation_axis, angle=math.radians(-90))
    uz = t.transform(local_z_axis)
    uy = rotation_axis
    # the block reference origin stays at the same location, no rotation needed
    wcs_insert = ocs.to_wcs(blockref.dxf.insert)
    # build new UCS to convert WCS locations and angles into OCS
    ucs = UCS(origin=wcs_insert, uy=uy, uz=uz)

    # set new OCS
    blockref.dxf.extrusion = ucs.uz
    # set new insert
    blockref.dxf.insert = ucs.to_ocs((0, 0, 0))
    # set new rotation: we do not rotate the block reference around the local z-axis,
    # but the new block x-axis (0 deg) differs from OCS x-axis and has to be adjusted
    blockref.dxf.rotation = ucs.to_ocs_angle_deg(0)

    doc.set_modelspace_vport(5)
    doc.saveas('ocs_insert.dxf')


if __name__ == '__main__':
    main()
