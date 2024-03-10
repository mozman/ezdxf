# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Iterable, Callable
from typing_extensions import override
import abc

from ezdxf import bbox
from ezdxf.entities import DXFEntity
from ezdxf.math import UVec, Vec2, BoundingBox2d
from ezdxf.query import EntityQuery


__all__ = [
    "SelectionShape",
    "Window",
    "Point",
    "Circle",
    "inside",
    "outside",
    "crossing",
]

# The basic selection functions "inside", "outside", "crossing", ... using the bounding
# box of DXF entities for selection.
# This is a design choice: performance and simplicity over accuracy
#
# A more accurate method based on the Primitive() class of the disassemble module using
# the path or mesh representation of DXF entities maybe added in the future.
# These extended selection functions will be called "inside_xt", "outside_xt", "crossing_xt", ...


class SelectionShape(abc.ABC):
    """AbstractBaseClass for selection shapes.

    It is guaranteed that all methods get an entity_bbox which has data!
    """

    @abc.abstractmethod
    def is_inside(self, entity_bbox: BoundingBox2d) -> bool: ...

    @abc.abstractmethod
    def is_outside(self, entity_bbox: BoundingBox2d) -> bool: ...

    @abc.abstractmethod
    def is_crossing(self, entity_bbox: BoundingBox2d) -> bool: ...


class Window(SelectionShape):
    """This selection shape tests entities against a rectangular and axis-aligned 2D
    window.  All entities are projected on the xy-plane.

    The selection tests are performed on the bounding box of the entities.
    This is a design choice: performance and simplicity over accuracy

    Args:
        p1: first corner of the window
        p2: second corner of the window
    """

    def __init__(self, p1: UVec, p2: UVec):
        self._bbox = BoundingBox2d((p1, p2))

    @override
    def is_inside(self, entity_bbox: BoundingBox2d) -> bool:
        return self._bbox.contains(entity_bbox)

    @override
    def is_outside(self, entity_bbox: BoundingBox2d) -> bool:
        return not self._bbox.has_overlap(entity_bbox)

    @override
    def is_crossing(self, entity_bbox: BoundingBox2d) -> bool:
        return self._bbox.has_overlap(entity_bbox)


class Point(SelectionShape):
    """This selection shape tests entities against a single point.  All entities are
    projected on the xy-plane.

    An entity is selected when the selection point is inside the bounding box of the entity.
    This is a design choice: performance and simplicity over accuracy

    By definition, nothing can be inside a dimensionless point and therefore everything
    is outside a point.

    Args:
        point: selection point
    """

    def __init__(self, point: UVec):
        self._point = Vec2(point)

    @override
    def is_inside(self, entity_bbox: BoundingBox2d) -> bool:
        return False

    @override
    def is_outside(self, entity_bbox: BoundingBox2d) -> bool:
        return True

    @override
    def is_crossing(self, entity_bbox: BoundingBox2d) -> bool:
        return entity_bbox.inside(self._point)


class Circle(SelectionShape):
    """This selection shape tests entities against a circle.  All entities are
    projected on the xy-plane.

    The selection tests are performed on the bounding box of the entities.
    This is a design choice: performance and simplicity over accuracy

    Args:
        center: center of the circle
        radius: radius of the circle
    """

    def __init__(self, center: UVec, radius: float):
        self._center = Vec2(center)
        self._radius = float(radius)
        r_vec = Vec2(self._radius, self._radius)
        self._bbox = BoundingBox2d((self._center - r_vec, self._center + r_vec))

    def _is_vertex_inside(self, v: Vec2) -> bool:
        return self._center.distance(v) <= self._radius

    @override
    def is_inside(self, entity_bbox: BoundingBox2d) -> bool:
        return all(self._is_vertex_inside(v) for v in entity_bbox.rect_vertices())

    @override
    def is_outside(self, entity_bbox: BoundingBox2d) -> bool:
        if not self._bbox.has_overlap(entity_bbox):
            return True
        return not self.is_crossing(entity_bbox)

    @override
    def is_crossing(self, entity_bbox: BoundingBox2d) -> bool:
        if any(self._is_vertex_inside(v) for v in entity_bbox.rect_vertices()):
            return True
        return self._is_vertex_inside(entity_bbox.center)


def inside(
    entities: Iterable[DXFEntity],
    shape: SelectionShape,
    cache: bbox.Cache | None = None,
) -> EntityQuery:
    """Returns all entities that are located inside the selection shape.

    Args:
        entities: iterable of DXFEntities
        shape: seclection shape
        cache: optional bounding box cache

    """
    return select_by_bbox(entities, shape.is_inside, cache)


def outside(
    entities: Iterable[DXFEntity],
    shape: SelectionShape,
    cache: bbox.Cache | None = None,
) -> EntityQuery:
    """Returns all entities that are located outside the selection shape.

    Args:
        entities: iterable of DXFEntities
        shape: seclection shape
        cache: optional bounding box cache

    """
    return select_by_bbox(entities, shape.is_outside, cache)


def crossing(
    entities: Iterable[DXFEntity],
    shape: SelectionShape,
    cache: bbox.Cache | None = None,
) -> EntityQuery:
    """Returns all entities that are overlapping the selection shape.

    Args:
        entities: iterable of DXFEntities
        shape: seclection shape
        cache: optional bounding box cache

    """
    return select_by_bbox(entities, shape.is_crossing, cache)


def select_by_bbox(
    entities: Iterable[DXFEntity],
    test_func: Callable[[BoundingBox2d], bool],
    cache: bbox.Cache | None = None,
) -> EntityQuery:
    """Calculates the bounding box for each entity and returns all entities for that the
    test function returns ``True``.

    Args:
        entities: iterable of DXFEntities
        func: test function which takes the bounding box of the entity as input and
            returns ``True`` if the entity is part of the selection.
        cache: optional bounding box cache

    """
    selection: list[DXFEntity] = []

    for entity in entities:
        extents = bbox.extents((entity,), fast=True, cache=cache)
        if not extents.has_data:
            continue
        if test_func(BoundingBox2d(extents)):
            selection.append(entity)
    return EntityQuery(selection)
