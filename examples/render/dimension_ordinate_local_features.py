# Copyright (c) 2021-2022, Manfred Moitzi
# License: MIT License

import pathlib
from ezdxf.math import Vec3, UCS
import ezdxf
from ezdxf.render import forms

# ------------------------------------------------------------------------------
# This example shows how to use ordinate dimension in UCS.
# ------------------------------------------------------------------------------

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


doc = ezdxf.new(setup=True)
msp = doc.modelspace()

# Create a special DIMSTYLE for "vertical" centered measurement text:
dimstyle = doc.dimstyles.duplicate_entry("EZDXF", "ORD_CENTER")
dimstyle.dxf.dimtad = 0  # "vertical" centered measurement text

# Add a rectangle: width=4, height = 2.5, lower left corner is WCS(x=2, y=3),
# rotated about 30 degrees:
origin = Vec3(2, 3)
msp.add_lwpolyline(
    forms.translate(forms.rotate(forms.box(4, 2.5), 30), origin),
    close=True
)

# Define the rotated local render UCS.
# The origin is the lower-left corner of the rectangle and the axis are
# aligned to the rectangle edges:
# The y-axis "uy" is calculated automatically by the right-hand rule.
ucs = UCS(origin, ux=Vec3.from_deg_angle(30), uz=(0, 0, 1))

# Add a x-type ordinate DIMENSION with local feature locations:
# the origin is now the origin of the UCS, which is (0, 0) the default value of
# "origin" and the feature coordinates are located in the UCS:
msp.add_ordinate_x_dim(
    # lower left corner
    feature_location=(0, 0),  # feature location in the UCS
    offset=(0.25, -2),  # # leader with a "knee"
    dimstyle="ORD_CENTER",
).render(
    ucs=ucs
)  # Important when using a render UCS!
msp.add_ordinate_x_dim(
    # lower right corner
    feature_location=(4, 0),  # feature location in the UCS
    offset=(0.25, -2),  # leader with a "knee"
    dimstyle="ORD_CENTER",
).render(
    ucs=ucs
)  # Important when using a render UCS!

# Add a y-type ordinate DIMENSION with local feature coordinates:
msp.add_ordinate_y_dim(
    # lower right corner
    feature_location=(4, 0),  # feature location in the UCS
    offset=(2, 0.25),  # leader with a "knee"
    dimstyle="ORD_CENTER",
).render(
    ucs=ucs
)  # Important when using a render UCS!
msp.add_ordinate_y_dim(
    # upper right corner
    feature_location=(4, 2.5),  # feature location in the UCS
    offset=(2, 0.25),  # leader with a "knee"
    dimstyle="ORD_CENTER",
).render(
    ucs=ucs
)  # Important when using a render UCS!
doc.saveas(CWD / "ord_local_features.dxf")
