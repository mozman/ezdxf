# Copyright (c) 2019-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.enums import TextEntityAlignment

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example adds a LEADER entity to the modelspace.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/leader.html
# ------------------------------------------------------------------------------

doc = ezdxf.new("R2007", setup=True)
msp = doc.modelspace()

# add default leader style
msp.add_leader(vertices=[(0, 0), (2, 2), (4, 2)])

# add leader with style override
msp.add_leader(
    vertices=[(10, 0), (12, 2), (14, 2)], override={"dimldrblk": "CLOSEDBLANK"}
)

msp.add_text(
    "Text",
    dxfattribs={
        "style": "OpenSans",
        "height": 0.25,
    },
).set_placement((4, 5), align=TextEntityAlignment.MIDDLE_LEFT)
msp.add_leader(vertices=[(0, 3), (2, 5), (4, 5)])

# For more information look at the Autodesk documentation.
# or https://atlight.github.io/formats/dxf-leader.html


filename = CWD / "leader.dxf"
doc.saveas(filename)
print(f"drawing {filename} created.")
