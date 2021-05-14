from pathlib import Path
import ezdxf
from ezdxf import zoom
from ezdxf.math import ConstructionArc, BSpline

DIR = Path("~/Desktop/Outbox/").expanduser()

doc = ezdxf.new()
msp = doc.modelspace()

# create the source ARC:
arc = msp.add_arc(
    (0, 0),
    radius=5,
    start_angle=15,
    end_angle=165,
    dxfattribs={
        "layer": "source arc",
        "color": ezdxf.const.RED,
    }
)

# create a SPLINE entity from ARC, in your scenario these are the source
# entities of your DXF document!
spline = msp.add_spline(dxfattribs={
    "layer": "B-Spline",
    "color": ezdxf.const.YELLOW,
})
# create a B-spline construction tool from ARC
arc_tool = arc.construction_tool()
bspline = BSpline.from_arc(arc_tool)
spline.apply_construction_tool(bspline)

# Recreate ARC from SPLINE, if you ASSUME or KNOW it is an ARC:
# for spline in msp.query("SPLINE):
#     ...
# 1. get the B-spline construction tool from the SPLINE entity
bspline = spline.construction_tool()
max_t = bspline.max_t

# calculate 3 significant points and 2 check points of the SPLINE:
start, chk1, middle, chk2, end = bspline.points([
    0, max_t * 0.25, max_t * 0.5, max_t * 0.75, max_t
])

# create an arc from 3 points:
arc_tool = ConstructionArc.from_3p(start, end, middle)
arc_tool.add_to_layout(msp, dxfattribs={
    "layer": "recreated arc",
    "color": ezdxf.const.MAGENTA,
})

# This only works for flat B-splines in the xy-plane, a.k.a. 2D splines!

# Check the assumption:
center = arc_tool.center
radius = arc_tool.radius
err = max(abs(radius - p.distance(center)) for p in (chk1, chk2))
print(f"max error: {err:.6f}")

# Warning: this does not proof that the assumption was correct, it is always
# possible to create a diverging B-spline which matches the check points:

foul = (4.5, 1)
fit_points = [start, foul, chk1, middle, chk2, end]
msp.add_spline(fit_points, dxfattribs={
    "layer": "foul B-spline",
    "color": ezdxf.const.RED,
})

# add check marks
for p in fit_points:
    msp.add_circle(p, radius=0.03, dxfattribs={"color": ezdxf.const.RED})

zoom.objects(msp, [arc])
doc.saveas(DIR / "arc_recreation.dxf")
