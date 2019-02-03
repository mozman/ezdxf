# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable
from ezdxf.math.vector import Vector

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


def closest_point(base: 'Vertex', points: Iterable['Vertex']) -> Vector:
    base = Vector(base)
    min_dist = None
    found = None
    for point in points:
        p = Vector(point)
        dist = (base - p).magnitude
        if (min_dist is None) or (dist < min_dist):
            min_dist = dist
            found = p
    return found
