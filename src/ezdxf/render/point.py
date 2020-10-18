#  Copyright (c) 2020, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, List
import math
from ezdxf.entities import factory
from ezdxf.math import Vector, UCS, NULLVEC

if TYPE_CHECKING:
    from ezdxf.entities import Point, DXFGraphic


def virtual_entities(point: 'Point', pdsize: float = 1,
                     pdmode: int = 0) -> List['DXFGraphic']:
    """ Yields point graphic as DXF primitives LINE and CIRCLE entities.
    The dimensionless point is rendered as zero-length line!

    Check for this condition::

        e.dxftype() == 'LINE' and e.dxf.start.isclose(e.dxf.end)

    if the rendering engine can't handle zero-length lines.


    Args:
        point: DXF POINT entity
        pdsize: point size in drawing units
        pdmode: point styling mode, see :class:`~ezdxf.entities.Point` class

    .. versionadded:: 0.15

    """

    def add_line_symmetrical(offset: Vector):
        dxfattribs['start'] = ucs.to_wcs(-offset)
        dxfattribs['end'] = ucs.to_wcs(offset)
        entities.append(factory.new('LINE', dxfattribs))

    def add_line(s: Vector, e: Vector):
        dxfattribs['start'] = ucs.to_wcs(s)
        dxfattribs['end'] = ucs.to_wcs(e)
        entities.append(factory.new('LINE', dxfattribs))

    center = point.dxf.location
    # This is not a real OCS! Defines just the point orientation,
    # location is in WCS!
    ocs = point.ocs()
    ucs = UCS(origin=center, ux=ocs.ux, uz=ocs.uz)

    # The point angle is clockwise oriented:
    ucs = ucs.rotate_local_z(math.radians(-point.dxf.angle))

    entities = []
    gfx = point.graphic_properties()

    radius = pdsize * 0.5
    has_circle = bool(pdmode & 32)
    has_square = bool(pdmode & 64)
    style = pdmode & 7

    dxfattribs = dict(gfx)
    if style == 0:  # . dimensionless point as zero-length line
        add_line_symmetrical(NULLVEC)
    # style == 1: no point symbol
    elif style == 2:  # + cross
        add_line_symmetrical(Vector(pdsize, 0))
        add_line_symmetrical(Vector(0, pdsize))
    elif style == 3:  # x cross
        add_line_symmetrical(Vector(pdsize, pdsize))
        add_line_symmetrical(Vector(pdsize, -pdsize))
    elif style == 4:  # ' tick
        add_line(NULLVEC, Vector(0, radius))
    if has_square:
        x1 = -radius
        x2 = radius
        y1 = -radius
        y2 = radius
        add_line(Vector(x1, y1), Vector(x2, y1))
        add_line(Vector(x2, y1), Vector(x2, y2))
        add_line(Vector(x2, y2), Vector(x1, y2))
        add_line(Vector(x1, y2), Vector(x1, y1))
    if has_circle:
        dxfattribs = dict(gfx)
        if point.dxf.hasattr('extrusion'):
            dxfattribs['extrusion'] = ocs.uz
            dxfattribs['center'] = ocs.from_wcs(center)
        else:
            dxfattribs['center'] = center
        dxfattribs['radius'] = radius
        entities.append(factory.new('CIRCLE', dxfattribs))

    # noinspection PyTypeChecker
    return entities
