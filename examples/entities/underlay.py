# Copyright (c) 2016-2022 Manfred Moitzi
# License: MIT License
import pathlib
import ezdxf
import shutil


CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to use UNDERLAY objects.
#
# This does not work reliable across CAD applications - don't use UNDERLAY objects!
# docs: https://ezdxf.mozman.at/docs/dxfentities/underlay.html
# tutorial: https://ezdxf.mozman.at/docs/tutorials/underlay.html
# ------------------------------------------------------------------------------

dwg = ezdxf.new("R2000")  # underlay requires the DXF R2000 format or newer
pdf_underlay_def = dwg.add_underlay_def(
    filename="underlay.pdf", name="1"
)  # name = page to display
dwf_underlay_def = dwg.add_underlay_def(
    filename="underlay.dwf", name="Underlay_R2013-Model"
)  # don't know how to get this name
dgn_underlay_def = dwg.add_underlay_def(
    filename="underlay.dgn", name="default"
)  # name = 'default' just works

# The (PDF)DEFINITION entity is like a block definition, it just defines the underlay
msp = dwg.modelspace()
# add first underlay
msp.add_underlay(pdf_underlay_def, insert=(0, 0, 0), scale=1.0)
# The (PDF)UNDERLAY entity is like the INSERT entity, it creates an underlay reference,
# and there can be multiple references to the same underlay in a drawing.
msp.add_underlay(pdf_underlay_def, insert=(10, 0, 0), scale=0.5, rotation=30)

# use dgn format
msp.add_underlay(dgn_underlay_def, insert=(0, 30, 0), scale=1.0)

# use dwf format
msp.add_underlay(dwf_underlay_def, insert=(0, 15, 0), scale=1.0)

# get existing underlay definitions, Important: UNDERLAYDEFs resides in the objects section
pdf_defs = dwg.objects.query(
    "PDFDEFINITION"
)  # get all pdf underlay defs in drawing

dwg.saveas(CWD / "underlay.dxf")

# copy underlay files to the same folder as the DXF file:
for name in ["underlay.pdf", "underlay.dwf", "underlay.dgn"]:
    shutil.copy(name, CWD / name)
