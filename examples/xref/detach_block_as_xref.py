#  Copyright (c) 2023, Manfred Moitzi
#  License: MIT License

import pathlib
import random

import ezdxf
from ezdxf.addons import odafc
from ezdxf.document import Drawing
from ezdxf import xref

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to detach a block definition as DXF or DWG external
# reference.
# ------------------------------------------------------------------------------


def get_random_point():
    x = random.randint(-100, 100)
    y = random.randint(-100, 100)
    return x, y


SAMPLE_COORDS = [get_random_point() for x in range(50)]
FLAG_SYMBOL = [(0, 0), (0, 5), (4, 3), (0, 3)]
FLAG_NAME = "Flag"


def make_doc() -> Drawing:
    doc = ezdxf.new("R2007")
    doc.layers.add("FLAGS")
    msp = doc.modelspace()

    flag = doc.blocks.new(name=FLAG_NAME)

    # Add dxf entities to the block (the flag).
    flag.add_polyline2d(FLAG_SYMBOL)
    flag.add_circle(center=(0, 0), radius=0.4, dxfattribs={"color": 1})

    # Create the ATTRIB templates as ATTDEF entities:
    flag.add_attdef(tag="NAME", insert=(0.5, -0.5), height=0.5, dxfattribs={"color": 3})
    flag.add_attdef(
        tag="XPOS", insert=(0.5, -1.0), height=0.25, dxfattribs={"color": 4}
    )
    flag.add_attdef(
        tag="YPOS", insert=(0.5, -1.5), height=0.25, dxfattribs={"color": 4}
    )

    for number, point in enumerate(SAMPLE_COORDS):
        # Create the value dictionary for the ATTRIB entities, key is the tag
        # name of the ATTDEF entity and the value is the content string of the
        # ATTRIB entity:
        values = {
            "NAME": f"P({number + 1})",
            "XPOS": f"x = {point[0]:.3f}",
            "YPOS": f"y = {point[1]:.3f}",
        }
        random_scale = 0.5 + random.random() * 2.0
        block_ref = msp.add_blockref(
            "FLAG", point, dxfattribs={"layer": "FLAGS", "rotation": -15}
        ).set_scale(random_scale)
        block_ref.add_auto_attribs(values)
    doc.set_modelspace_vport(height=200)
    return doc


def detach_block_as_dxf(doc: Drawing, block_name: str) -> None:
    flag = doc.blocks.get(block_name)
    if flag is None:
        print(f"Block definition '{block_name}' not found.")
        return
    xref_doc = xref.detach(flag, xref_filename="flag_block.dxf")
    xref_doc.saveas(CWD / "flag_block.dxf")
    # Remove destroyed entities of the block definition from entity database,
    # optional but recommended.
    doc.entitydb.purge()
    doc.saveas(CWD / "attached_dxf_xref.dxf")


def detach_block_as_dwg(doc: Drawing, block_name: str) -> None:
    flag = doc.blocks.get(block_name)
    if flag is None:
        print(f"Block definition '{block_name}' not found.")
        return
    xref_doc = xref.detach(flag, xref_filename="flag_block.dwg")
    odafc.export_dwg(xref_doc, CWD / "flag_block.dwg")
    # Remove destroyed entities of the block definition from entity database,
    # optional but recommended.
    doc.entitydb.purge()
    doc.saveas(CWD / "attached_dwg_xref.dxf")


def make_dxf_xref():
    doc = make_doc()
    # This works with BricsCAD and maybe with other user-friendly CAD applications
    # but NOT with stubborn Autodesk products that don't support DXF files as XREFs.
    detach_block_as_dxf(doc, FLAG_NAME)


def make_dwg_xref():
    doc = make_doc()
    # This works with all CAD applications but requires an installed
    # Open Design Alliance (ODA) FileConverter!
    # https://www.opendesign.com/guestfiles/oda_file_converter
    detach_block_as_dwg(doc, FLAG_NAME)


if __name__ == "__main__":
    make_dxf_xref()
    make_dwg_xref()
