# Copyright (c) 2021-2022, Manfred Moitzi
# License: MIT License

import pathlib
from ezdxf.math import Vec3
import ezdxf
from ezdxf.render import forms

# ------------------------------------------------------------------------------
# This example shows how to use ordinate dimension in WCS.
#
# tutorial: https://ezdxf.mozman.at/docs/tutorials/ordinate_dimension.html
# ------------------------------------------------------------------------------

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")


# Use argument setup=True to setup the default dimension styles.
doc = ezdxf.new(setup=True)

# Add new entities to the modelspace:
msp = doc.modelspace()
# Add a rectangle: width=4, height = 2.5, lower left corner is WCS(x=2, y=3)
origin = Vec3(2, 3)
msp.add_lwpolyline(
    forms.translate(forms.box(4, 2.5), origin),
    close=True
)

# Add a x-type ordinate DIMENSION with global feature locations:
msp.add_ordinate_x_dim(
    # lower left corner
    feature_location=origin + (0, 0),  # feature location in the WCS
    offset=(0, -2),  # end of leader, relative to the feature location
    origin=origin,
).render()
msp.add_ordinate_x_dim(
    # lower right corner
    feature_location=origin + (4, 0),  # feature location in the WCS
    offset=(0, -2),
    origin=origin,
).render()

# Add a y-type ordinate DIMENSION with global feature locations:
msp.add_ordinate_y_dim(
    # lower right corner
    feature_location=origin + (4, 0),  # feature location in the WCS
    offset=(2, 0),
    origin=origin,
).render()
msp.add_ordinate_y_dim(
    # upper right corner
    feature_location=origin + (4, 2.5),  # feature location in the WCS
    offset=(2, 0),
    origin=origin,
).render()

# Necessary second step to create the BLOCK entity with the dimension geometry.
# Additional processing of the DIMENSION entity could happen between adding
# the entity and the rendering call.
doc.saveas(CWD / "ord_global_features.dxf")

