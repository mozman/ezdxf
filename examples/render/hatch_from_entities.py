#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf.render.forms import box, translate
from ezdxf import disassemble
from ezdxf import path

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to create a new HATCH entity from existing
# DXF entities, which is similar to applying then HATCH command to some DXF
# entities in CAD applications
#
# docs:
# disassemble module: https://ezdxf.mozman.at/docs/disassemble.html
# path sub-package: https://ezdxf.mozman.at/docs/path.html
# ------------------------------------------------------------------------------


def main():
    doc = ezdxf.new()
    doc.layers.new("FORMS", dxfattribs={"color": 1})
    doc.layers.new("HATCHES")

    msp = doc.modelspace()
    attribs = {"layer": "FORMS"}

    # Create DXF primitives:
    msp.add_circle((2, 3), radius=2, dxfattribs=attribs)

    # Ellipse with hole:
    msp.add_ellipse((5, 0), major_axis=(3, 1), ratio=0.5, dxfattribs=attribs)
    msp.add_circle((5, 0), radius=1.5, dxfattribs=attribs)

    # Rectangle with a hole
    rect = translate(box(3, 2), (3, 6))
    msp.add_lwpolyline(rect, close=True, dxfattribs=attribs)
    hole = translate(box(2, 1), (3.4, 6.4))
    msp.add_lwpolyline(hole, close=True, dxfattribs=attribs)

    # Convert entities to primitives
    primitives = disassemble.to_primitives(msp)

    # Collect paths from primitives:
    paths = [p.path for p in primitives if p.path]

    # Render these paths as HATCH entities
    path.render_hatches(msp, paths, dxfattribs={"layer": "HATCHES", "color": 2})

    doc.set_modelspace_vport(15, (4, 4))
    doc.saveas(CWD / "hatches_from_entities.dxf")


if __name__ == "__main__":
    main()
