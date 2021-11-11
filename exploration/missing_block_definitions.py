#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from pathlib import Path
import ezdxf

DIR = Path("~/Desktop/Outbox").expanduser()

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

doc.saveas(DIR / "missing_block_definitions.dxf")
