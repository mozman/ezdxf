# Copyright (c) 2016-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example adds a circle to the modelspace.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/circle.html
# ------------------------------------------------------------------------------

# setup=True is required to get the DASHED linetype.
doc = ezdxf.new("R12", setup=True)
modelspace = doc.modelspace()
modelspace.add_circle(
    center=(0, 0),
    radius=1.5,
    dxfattribs={
        "layer": "test",
        "linetype": "DASHED",
    },
)

filename = CWD / "circle.dxf"
doc.saveas(filename)
print(f"drawing '{filename}' created.")
