# Purpose: draw a maurer rose with polylines
# https://en.wikipedia.org/wiki/Maurer_rose
# Created: 13.10.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
from typing import Iterable, Tuple
import math
import ezdxf

N = 6  # The rose has n petals if N is odd, and 2N petals if N is even.
D = 71  # delta angle in degrees
TWO_PI = math.pi * 2
STEP360 = TWO_PI / 360


def maurer_rose(n: int, d: int, radius: float) -> Iterable[Tuple[float, float]]:
    i = 0
    while i < TWO_PI:
        k = i * d
        r = radius * math.sin(n * k)
        x = r * math.cos(k)
        y = r * math.sin(k)
        yield x, y
        i += STEP360


def maurer_rose_outline(n: int, radius: float) -> Iterable[Tuple[float, float]]:
    i = 0
    while i < TWO_PI:
        r = radius * math.sin(n * i)
        x = r * math.cos(i)
        y = r * math.sin(i)
        yield x, y
        i += STEP360


def main(filename: str, n: int, d: int) -> None:
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_lwpolyline(maurer_rose_outline(n, 250), dxfattribs={'closed': True, 'color': 1})
    msp.add_lwpolyline(maurer_rose(n, d, 250), dxfattribs={'closed': True, 'color': 5})
    doc.saveas(filename)


if __name__ == '__main__':
    main('maurer_rose.dxf', N, D)
