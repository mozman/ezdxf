# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Sequence
import math
from ezdxf.math import UVec, Vec2


def points(
    points: UVec,
    segment_length: float,
    bulge: float = 0.5,
    start_width: float = 0.0,
    end_width: float = 0.0,
) -> list[Sequence[float]]:
    """Returns the points for a LWPOLYLINE entity to render a revision cloud, similar to 
    the REVCLOUD command in CAD applications.

    Args:
        points: corner points of a polygon
        segment_length: approximate segment length
        bulge: LWPOLYLINE bulge value
        start_width: start width of the segment arc
        end_width: end width of the segment arc

    """
    if segment_length < 1e-6:
        raise ValueError("segment length too small.")
    
    vertices = Vec2.list(points)
    if len(vertices) < 3:
        raise ValueError("3 or more points required.")
    
    if not vertices[0].isclose(vertices[-1]):
        vertices.append(vertices[0])

    if len(vertices) < 4:
        raise ValueError("3 or more points required.")

    lw_points: list[Sequence[float]] = []
    for s, e in zip(vertices, vertices[1:]):
        lw_points.append((s.x, s.y, start_width, end_width, bulge))
        diff = e - s
        length = diff.magnitude
        if length <= segment_length:
            continue

        count = math.ceil(length / segment_length)
        _segment_length = length / count
        offset = diff.normalize(_segment_length)
        for _ in range(count):
            s += offset
            lw_points.append((s.x, s.y, start_width, end_width, bulge))
    return  lw_points