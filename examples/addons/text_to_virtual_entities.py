# Copyright (c) 2021-2022, Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
from ezdxf.addons import text2path
from ezdxf import zoom, disassemble
from ezdxf.lldxf import const

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to convert TEXT entities to outline paths.
#
# docs: https://ezdxf.mozman.at/docs/addons/text2path.html
# ------------------------------------------------------------------------------

EXAMPLES = pathlib.Path(__file__).parent.parent.parent / "examples_dxf"
FILE1 = "text_mirror_true_type_font.dxf"
FILE2 = "text_oblique_rotate.dxf"

FILE = FILE2


def main():
    doc = ezdxf.readfile(EXAMPLES / FILE)
    doc.layers.new("OUTLINE", dxfattribs={"color": 1})
    doc.layers.new("BBOX", dxfattribs={"color": 5})
    msp = doc.modelspace()
    text_entities = msp.query("TEXT")

    # Convert TEXT entities into SPLINE and POLYLINE entities:
    kind = text2path.Kind.SPLINES
    for text in text_entities:
        for e in text2path.virtual_entities(text, kind=kind):
            e.dxf.layer = "OUTLINE"
            e.dxf.color = const.BYLAYER
            msp.add_entity(e)

    # Add bounding boxes
    attrib = {"layer": "BBOX"}
    boxes = []

    # The "primitive" representation for TEXT entities is the bounding box:
    for prim in disassemble.to_primitives(text_entities):
        p = msp.add_lwpolyline(prim.vertices(), dxfattribs=attrib)
        boxes.append(p)

    # Zoom on bounding boxes (fast):
    zoom.objects(msp, boxes, factor=1.1)
    doc.saveas(CWD / FILE)


if __name__ == "__main__":
    main()
