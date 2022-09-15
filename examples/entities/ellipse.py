# Copyright (c) 2016-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example adds an ellipse to the modelspace.
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
    dxfattribs={
        "layer": "test",
        "linetype": "DASHED",
    },
)

filename = CWD / "ellipse.dxf"
doc.saveas(filename)
print(f"drawing '{filename}' created.")
