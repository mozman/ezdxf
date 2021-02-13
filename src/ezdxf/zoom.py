#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable

from ezdxf.math import Vertex, Vec2, BoundingBox2d
from ezdxf.layouts import Layout
from ezdxf.entities import DXFEntity
from ezdxf import bbox

__all__ = ["center", "entities", "extends", "window"]


def center(layout: Layout, point: Vertex, height: float):
    """ Resets the active viewport center of `layout` to the given `point`,
    argument `height` defines the viewport height.
    Replaces the current viewport configuration by a single window
    configuration.

    """
    doc = layout.doc
    if doc:
        if layout.name == 'Model':
            doc.set_modelspace_vport(height, Vec2(point))
        else:
            raise NotImplementedError("Only model space support yet.")


def guess_height(size):
    width = size.x
    height = size.y
    # expected aspect ratio: 16:10
    return max(width / 2.0, height)


def zoom_to_entities(layout: Layout, entities: Iterable[DXFEntity], factor):
    extents = bbox.extends(entities)
    if extents.has_data:
        height = guess_height(extents.size)
        center(layout, extents.center, height * factor)


def objects(layout: Layout, entities: Iterable[DXFEntity], factor: float = 1):
    """ Resets the active viewport limits of `layout` to the extends of the
    given `entities`. Only entities in the given `layout` are taken into
    account. The argument `factor` scales the viewport limits.
    Replaces the current viewport configuration by a single window
    configuration.

    """
    owner = layout.layout_key
    content = (e for e in entities if e.dxf.owner == owner)
    zoom_to_entities(layout, content, factor)


def extends(layout: Layout, factor: float = 1):
    """ Resets the active viewport limits of `layout` to the extents of all
    entities in this `layout`. The argument `factor` scales the viewport limits.
    Replaces the current viewport configuration by a single window
    configuration.

    """
    zoom_to_entities(layout, layout, factor)


def window(layout: Layout, p1: Vertex, p2: Vertex):
    """ Resets the active viewport limits of `layout` to the lower left corner
    `p1` and the upper right corner `p2`.
    Replaces the current viewport configuration by a single window
    configuration.

    """
    extents = BoundingBox2d([p1, p2])
    center(layout, extents.center, extents.size.y)
