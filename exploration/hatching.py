#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

from pathlib import Path
import ezdxf
from ezdxf.math import Vec2
from ezdxf.render import forms, hatching

CWD = Path("~/Desktop/Outbox").expanduser()
if not CWD.exists():
    CWD = Path(".")


def polygon_hatching(filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()
    polygon = Vec2.list(
        forms.gear(16, top_width=1, bottom_width=3, height=2, outside_radius=10)
    )
    hole = list(forms.circle(17, radius=4))
    hole1 = Vec2.list(forms.translate(hole, (-2, -2)))
    hole2 = Vec2.list(forms.translate(hole, (2, 2)))
    msp.add_lwpolyline(polygon, close=True)
    msp.add_lwpolyline(hole1, close=True)
    msp.add_lwpolyline(hole2, close=True)
    baseline = hatching.HatchBaseLine(
        Vec2(), direction=Vec2(1, 1), offset=Vec2(-1, 1)
    )
    for line in hatching.hatch_polygons(baseline, [polygon, hole1, hole2]):
        msp.add_line(line.start, line.end)
    doc.saveas(CWD / filename)


if __name__ == "__main__":
    polygon_hatching("polygon_hatching.dxf")
