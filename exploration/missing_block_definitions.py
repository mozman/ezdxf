#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# Create a DXF document with missing BLOCK definitions
# to see how AutoCAD/BricsCAD reacts:
doc = ezdxf.new()
msp = doc.modelspace()

# HEADER variables for arrows:
doc.header["$DIMBLK"] = "DoesNotExist"
doc.header["$DIMBLK1"] = "DoesNotExist"
doc.header["$DIMBLK2"] = "DoesNotExist"
doc.header["$DIMLDRBLK"] = "DoesNotExist"

# INSERT without a BLOCK definition:
msp.add_blockref("TEST", (0, 0))

doc.saveas(CWD / "missing_block_definitions.dxf")
