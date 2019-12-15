# Created: 15.12.2019
# Copyright (c) 2019, Manfred Moitzi
# License: MIT License
"""
A collection of construction tools, some in a CAD-like manner, but far away form real CAD tools.

"""
from typing import TYPE_CHECKING, Iterable
from ezdxf.math import Vec2
from ezdxf.math.line import ConstructionRay, ParallelRaysError

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex


def offset_vertices_2d(vertices: Iterable['Vertex'], offset: float, closed=False) -> Iterable['Vec2']:
    """
    Yields vertices of the offset line to the shape defined by `vertices`. The source shape consist
    of straight segments and is located in the xy-plane, the z-axis of input vertices is ignored.
    Takes closed shapes into account if argument `closed` is ``True``, which yields intersection of first and last
    offset segment as first vertex for a closed shape. For closed shapes the first and last vertex can be equal,
    else an implicit closing segment from last to first vertex is added.
    A shape  with equal first and last vertex is not handled automatically as closed shape.

    .. warning::

        Adjacent collinear segments in `opposite` directions, same as a turn by 180 degree (u-turn), leads to
        incorrect results.

    Args:
        vertices: source shape defined by vertices
        offset: line offset in direction of shape segments defined by vertices order, offset > ``0`` is 'left' of line
                segment, offset < ``0`` is 'right' of line segment
        closed: ``True`` to handle as closed shape

    """
    vertices = list(Vec2(v) for v in vertices)
    if len(vertices) < 2:
        raise ValueError('2 or more vertices required.')

    if closed and not vertices[0].isclose(vertices[-1]):
        # append first vertex as last vertex to close shape
        vertices.append(vertices[0])

    # create offset segments
    offset_segments = list()
    for start, end in zip(vertices[:-1], vertices[1:]):
        offset_vec = (end - start).orthogonal().normalize(offset)
        offset_segments.append((start + offset_vec, end + offset_vec))

    if closed:  # insert last segment also as first segment
        offset_segments.insert(0, offset_segments[-1])

    # first offset vertex = start point of first segment for open shapes
    if not closed:
        yield offset_segments[0][0]

    # yield intersection points of offset_segments
    if len(offset_segments) > 1:
        for (start1, end1), (start2, end2) in zip(offset_segments[:-1], offset_segments[1:]):
            if end1.isclose(start2):
                # segments are parallel, no intersection point exist
                yield end1
            else:
                try:
                    yield ConstructionRay(start1, end1).intersect(ConstructionRay(start2, end2))
                except ParallelRaysError:
                    # for closed shapes with first segment is collinear to last segment
                    yield start2

    # last offset vertex = end point of last segment for open shapes
    if not closed:
        yield offset_segments[-1][1]
