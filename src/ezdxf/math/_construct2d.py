# Copyright (c) 2010-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable

from ezdxf.acc import USE_C_EXT
if USE_C_EXT:
    from ezdxf.acc.vector import Vec2
else:
    from ._vector import Vec2

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


def has_clockwise_orientation(vertices: Iterable['Vertex']) -> bool:
    """ Returns True if 2D `vertices` have clockwise orientation. Ignores
    z-axis of all vertices.

    Args:
        vertices: iterable of :class:`Vec2` compatible objects

    Raises:
        ValueError: less than 3 vertices

    """
    vertices = Vec2.list(vertices)
    if len(vertices) < 3:
        raise ValueError('At least 3 vertices required.')

    # Close polygon:
    if not vertices[0].isclose(vertices[-1]):
        vertices.append(vertices[0])

    return sum(
        (p2.x - p1.x) * (p2.y + p1.y)
        for p1, p2 in zip(vertices, vertices[1:])
    ) > 0
