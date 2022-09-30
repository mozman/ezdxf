import pathlib
import ezdxf
from ezdxf.upright import upright

from ezdxf.math import Matrix44

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


doc = ezdxf.new()
msp = doc.modelspace()

arc = msp.add_arc(
    (5, 0),
    radius=5,
    start_angle=-90,
    end_angle=90,
    dxfattribs={"color": ezdxf.const.RED},
)
# draw lines to the start- and end point of the ARC
msp.add_line((0, 0), arc.start_point, dxfattribs={"color": ezdxf.const.GREEN})
msp.add_line((0, 0), arc.end_point, dxfattribs={"color": ezdxf.const.BLUE})

# copy arc
mirrored_arc = arc.copy()
msp.add_entity(mirrored_arc)

# mirror copy
mirrored_arc.transform(Matrix44.scale(-1, 1, 1))

# This creates an inverted extrusion vector:
assert mirrored_arc.dxf.extrusion.isclose((0, 0, -1))

start_point_inv = mirrored_arc.start_point
end_point_inv = mirrored_arc.end_point

upright(mirrored_arc)
# OCS is aligned with WCS:
assert mirrored_arc.dxf.extrusion.isclose((0, 0, 1))

# start- and end points are swapped after applying upright()
assert mirrored_arc.start_point.isclose(end_point_inv)
assert mirrored_arc.end_point.isclose(start_point_inv)

# draw lines to the start- and end point of the mirrored ARC
msp.add_line((0, 0), mirrored_arc.start_point, dxfattribs={"color": ezdxf.const.GREEN})
msp.add_line((0, 0), mirrored_arc.end_point, dxfattribs={"color": ezdxf.const.BLUE})


doc.set_modelspace_vport(15)
doc.saveas(CWD / "upright_arc.dxf")
