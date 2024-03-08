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
    lw_points = revcloud.points(
        [(0, 0), (1, 0), (1, 1), (0, 1)],
        segment_length=0.1,
        bulge=0.5,
        start_width=0.01,
        end_width=0,
    )
    msp.add_lwpolyline(lw_points)
    doc.saveas(CWD / "revcloud.dxf")


if __name__ == "__main__":
    main()
