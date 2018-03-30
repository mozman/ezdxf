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
    axis = Vector(1, 0, -1)
    def_point = Vector(3, 10, 4)
    ucs = UCS.from_x_axis_and_point_in_xz(origin, axis=axis, point=def_point)

    add_axis(target=X_AXIS * AXIS_LENGTH, color=1)
    add_axis(target=Y_AXIS * AXIS_LENGTH, color=3)
    add_axis(target=Z_AXIS * AXIS_LENGTH, color=5)
    msp.add_point(location=def_point, dxfattribs={'color': 2})
    circle = msp.add_circle(center=origin, radius=1, dxfattribs={'color': 2})
    circle.dxf.extrusion = ucs.uz
    ocs = circle.ocs()
    circle.dxf.center = ocs.wcs_to_ocs(origin)
    dwg.saveas(filename)


if __name__ == '__main__':
    main("using_ucs.dxf")
