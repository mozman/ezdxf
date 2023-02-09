# Copyright (c) 2017-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.math import UCS

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to place a MTEXT entity in 3D space.
#
# docs: https://ezdxf.mozman.at/docs/dxfentities/mtext.html
# tutorial: https://ezdxf.mozman.at/docs/tutorials/mtext.html
# ------------------------------------------------------------------------------


def place_by_extrusion_vector():
    doc = ezdxf.new("R2000")
    modelspace = doc.modelspace()
    modelspace.add_mtext(
        "This is a text in the YZ-plane",
        dxfattribs={
            "width": 12,  # reference rectangle width
            "text_direction": (0, 1, 0),  # write in y direction
            "extrusion": (1, 0, 0),  # normal vector of the text plane
        },
    )
    doc.saveas(CWD / "mtext_extrusion_vector.dxf")


def place_by_ucs():
    doc = ezdxf.new("R2000")
    modelspace = doc.modelspace()
    # place the MTEXT in the xy-plane of the UCS
    mtext = modelspace.add_mtext(
        "This is a text in the YZ-plane",
        dxfattribs={
            "width": 12,  # reference rectangle width
            "text_direction": (1, 0, 0),  # write in x direction
        },
    )
    # define the ucs:
    # x-axis = WCS y-axis; z-axis = WCS x-axis
    ucs = UCS(ux=(0, 1, 0), uz=(1, 0, 0))
    mtext.transform(ucs.matrix)
    doc.saveas(CWD / "mtext_ucs.dxf")


if __name__ == '__main__':
    place_by_extrusion_vector()
    place_by_ucs()
