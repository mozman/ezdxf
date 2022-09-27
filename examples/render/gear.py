#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
import pathlib
import ezdxf
from ezdxf.render.forms import gear

CWD = pathlib.Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = pathlib.Path(".")

# ------------------------------------------------------------------------------
# This example shows how to create gear-like shaped polyline.
#
# docs: https://ezdxf.mozman.at/docs/render/forms.html#ezdxf.render.forms.gear
# ------------------------------------------------------------------------------

doc = ezdxf.new()
msp = doc.modelspace()
msp.add_lwpolyline(
    gear(16, top_width=1, bottom_width=3, height=2, outside_radius=10),
    close=True,
)
doc.saveas(CWD / "gear.dxf")
