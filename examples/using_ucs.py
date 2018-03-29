import ezdxf
from ezdxf.algebra import Vector, UCS, X_AXIS, Y_AXIS, Z_AXIS

AXIS_LENGTH = 5.


def main(filename):
    def add_axis(target, color=1):
        start = ucs.ucs_to_wcs((0, 0, 0))
        end = ucs.ucs_to_wcs(target)
        msp.add_line(start, end, dxfattribs={'color': color})

    dwg = ezdxf.new('R2010')
    msp = dwg.modelspace()
    origin = Vector(3, 3, 3)
    x_axis = Vector(1, 0, 0)
    def_point_in_xy_plane = Vector(3, 10, 4)
    local_vec = def_point_in_xy_plane - origin

    z_axis = x_axis.cross(local_vec)
    ucs = UCS(origin=origin, ux=x_axis, uz=z_axis)

    add_axis(target=X_AXIS * AXIS_LENGTH, color=1)
    add_axis(target=Y_AXIS * AXIS_LENGTH, color=3)
    add_axis(target=Z_AXIS * AXIS_LENGTH, color=5)
    msp.add_point(location=def_point_in_xy_plane, dxfattribs={'color': 2})
    msp.add_line(
        start=ucs.ucs_to_wcs((AXIS_LENGTH, 0, 0)),
        end=ucs.ucs_to_wcs((0, AXIS_LENGTH, 0)),
        dxfattribs={
            'color': 7
        }
    )
    circle = msp.add_circle(center=origin, radius=1, dxfattribs={'color': 2})
    circle.dxf.extrusion = ucs.uz
    ocs = circle.ocs()
    circle.dxf.center = ocs.wcs_to_ocs(origin)
    dwg.saveas(filename)


if __name__ == '__main__':
    main("using_ucs.dxf")
