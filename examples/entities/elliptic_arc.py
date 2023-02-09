# Copyright (c) 2016-2022 Manfred Moitzi
# License: MIT License
import pathlib
import math
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example adds an elliptic arc to the modelspace.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/ellipse.html
# ------------------------------------------------------------------------------

# setup=True is required to get the DASHED linetype.
doc = ezdxf.new("R2000", setup=True)
modelspace = doc.modelspace()
modelspace.add_ellipse(
    center=(0, 0),
    major_axis=(3, 1),
    ratio=0.65,
    start_param=0,  # in range from 0 to 2*pi
    end_param=math.pi,   # in range from 0 to 2*pi
    dxfattribs={
        "layer": "test",
        "linetype": "DASHED",
    },
)
# The curve is always drawn counter-clockwise from the start param to the
# end param.

filename = CWD / "ellipse.dxf"
doc.saveas(filename)
print(f"drawing '{filename}' created.")
