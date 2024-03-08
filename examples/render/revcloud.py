# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from pathlib import Path
import ezdxf
from ezdxf.render import revcloud

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")


def main():
    doc = ezdxf.new()
    msp = doc.modelspace()
    length = 0.1
    lw_points = revcloud.points(
        [(0, 0), (1, 0), (1, 1), (0, 1)],
        segment_length=length,
        bulge=0.5,
        start_width=0.01,
        end_width=0,
    )
    
    lwp = msp.add_lwpolyline(lw_points)
    # You can add XDATA for CAD applications, but it's not required and has no 
    # advantages - BricsCAD still does not recognize such entities as REVCLOUD entities.
    lwp.set_xdata("RevcloudProps", [(1070, 0), (1040, length)])
    doc.appids.add("RevcloudProps")
    doc.saveas(CWD / "revcloud.dxf")


if __name__ == "__main__":
    main()
