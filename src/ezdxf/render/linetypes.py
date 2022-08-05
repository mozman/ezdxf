#  Copyright (c) 2020-2022, Manfred Moitzi
#  License: MIT License
from typing import Iterable
from ezdxf.math import UVec
from ._linetypes import _LineTypeRenderer, LineSegment


class LineTypeRenderer(_LineTypeRenderer):
    def line_segments(self, vertices: Iterable[UVec]) -> Iterable[LineSegment]:
        last = None
        for vertex in vertices:
            if last is not None:
                yield from self.line_segment(last, vertex)
            last = vertex
