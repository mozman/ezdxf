#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License
from typing import Iterable, List
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
    hole = list(forms.circle(16, radius=4))
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


def draw(d:str) -> List[Vec2]:
    point = Vec2()
    points = [point]
    for cmd in d.split(","):
        cmd = cmd.strip()
        if cmd[0] == "h":
            point += Vec2(float(cmd[1:]), 0)
        elif cmd[0] == "v":
            point += Vec2(0, float(cmd[1:]))
        elif cmd[0] == "q":
            direction = cmd[1]
            l = float(cmd[2:])
            if direction == "1":
                point += Vec2(l, l)
            elif direction == "2":
                point += Vec2(-l, l)
            elif direction == "3":
                point += Vec2(-l, -l)
            else:
                point += Vec2(l, -l)
        points.append(point)
    return points


def collinear_hatching(filename: str):
    doc = ezdxf.new()
    msp = doc.modelspace()
    polygons = [
        draw("h+10, v+10, h-10"),
        draw("h+2, v+2, h+2, v-2, h+6, v+10, h-2, v-2, h-2, v+2, h-6"),
        draw("h+2, v+2, h+2, v+2, h+2, v-4, h+4, v+10, h-2, v-2, h-2, v-2, h-2, v+4, h-4"),
        draw("h+2, v-2, h+2, v-2, h+2, v+4, h+4, v+10, h-2, v+2, h-2, v+2, h-2, v-4, h-4"),
        draw("h+2, v+2, h+2, v-2, h+2, v+3, h+2, v-3, h+2, v+10, h-10"),
        draw("h+3, q1+2, q4+2, h+3, v+10, q3+2, q2+2, h-2, q3+2, q2+2")
    ]
    for index, polygon in enumerate(polygons):
        polygon = Vec2.list(forms.translate(polygon, Vec2(12 * index, 0)))
        msp.add_lwpolyline(
            polygon,
            close=True,
            dxfattribs={"color": ezdxf.colors.BLUE, "layer": "POLYGON"},
        )
        baseline = hatching.HatchBaseLine(
            Vec2(), direction=Vec2(1, 0), offset=Vec2(0, 1)
        )
        for line in hatching.hatch_polygons(baseline, [polygon]):
            msp.add_line(
                line.start,
                line.end,
                dxfattribs={
                    "color": ezdxf.colors.YELLOW,
                    "layer": "HATCH",
                },
            )
    doc.saveas(CWD / filename)


if __name__ == "__main__":
    polygon_hatching("polygon_hatching.dxf")
    collinear_hatching("collinear_hatching.dxf")
