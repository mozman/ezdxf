# Copyright (c) 2024, Manfred Moitzi
# License: MIT License
from __future__ import annotations
from typing import Iterable, Callable
from typing_extensions import override
import abc

from ezdxf import bbox
from ezdxf.entities import DXFEntity
from ezdxf.math import UVec, Vec2, BoundingBox2d, is_point_in_polygon_2d
from ezdxf.math.clipping import CohenSutherlandLineClipping2d
from ezdxf.query import EntityQuery


__all__ = [
    "Window",
    "Circle",
    "Polygon",
    "bbox_inside",
    "bbox_outside",
    "bbox_overlap",
    "bbox_chained",
    "bbox_crosses_fence",
    "point_in_bbox",
]


class SelectionShape(abc.ABC):
    """AbstractBaseClass for selection shapes.

    It is guaranteed that all methods get an entity_bbox which has data!
    """

    @abc.abstractmethod
    def is_inside_bbox(self, entity_bbox: BoundingBox2d) -> bool: ...

    @abc.abstractmethod
    def is_outside_bbox(self, entity_bbox: BoundingBox2d) -> bool: ...

    @abc.abstractmethod
    def is_overlapping_bbox(self, entity_bbox: BoundingBox2d) -> bool: ...


class Window(SelectionShape):
    """This selection shape tests entities against a rectangular and axis-aligned 2D
    window.  All entities are projected on the xy-plane.

    Args:
        p1: first corner of the window
        p2: second corner of the window
    """

    def __init__(self, p1: UVec, p2: UVec):
        self._bbox = BoundingBox2d((p1, p2))

    @override
    def is_inside_bbox(self, entity_bbox: BoundingBox2d) -> bool:
        return self._bbox.contains(entity_bbox)

    @override
    def is_outside_bbox(self, entity_bbox: BoundingBox2d) -> bool:
        return not self._bbox.has_overlap(entity_bbox)

    @override
    def is_overlapping_bbox(self, entity_bbox: BoundingBox2d) -> bool:
        return self._bbox.has_overlap(entity_bbox)


class Circle(SelectionShape):
    """This selection shape tests entities against a circle.  All entities are
    projected on the xy-plane.

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
    def is_inside_bbox(self, entity_bbox: BoundingBox2d) -> bool:
        return all(self._is_vertex_inside(v) for v in entity_bbox.rect_vertices())

    @override
    def is_outside_bbox(self, entity_bbox: BoundingBox2d) -> bool:
        return not self.is_overlapping_bbox(entity_bbox)

    @override
    def is_overlapping_bbox(self, entity_bbox: BoundingBox2d) -> bool:
        if not self._bbox.has_overlap(entity_bbox):
            return False
        if any(self._is_vertex_inside(v) for v in entity_bbox.rect_vertices()):
            return True
        return self._is_vertex_inside(entity_bbox.center)


class Polygon(SelectionShape):
    """This selection shape tests entities against an arbitrary closed polygon.
    All entities are projected on the xy-plane. **Convex** polygons may not work as
    expected.
    """

    def __init__(self, vertices: Iterable[UVec]):
        v = Vec2.list(vertices)
        if len(v) < 3:
            raise ValueError("3 or more vertices required")
        if v[0].isclose(v[-1]):
            v.pop()  # open polygon
        if len(v) < 3:
            raise ValueError("3 or more vertices required")
        self._vertices: list[Vec2] = v
        self._bbox = BoundingBox2d(self._vertices)

    def _has_intersection(self, extmin: Vec2, extmax: Vec2) -> bool:
        cs = CohenSutherlandLineClipping2d(extmin, extmax)
        vertices = self._vertices
        for index, end in enumerate(vertices):
            if cs.clip_line(vertices[index - 1], end):
                return True
        return False

    @override
    def is_inside_bbox(self, entity_bbox: BoundingBox2d) -> bool:
        if not self._bbox.has_overlap(entity_bbox):
            return False
        if any(
            is_point_in_polygon_2d(v, self._vertices) < 0  # outside
            for v in entity_bbox.rect_vertices()
        ):
            return False

        # Additional test for concave polygons. This may not cover all concave polygons.
        # Is any point of the polygon (strict) inside the entity bbox?
        min_x, min_y = entity_bbox.extmin
        max_x, max_y = entity_bbox.extmax
        # strict inside test: points on the boundary line do not count as inside
        return not any(
            (min_x < v.x < max_x) and (min_y < v.y < max_y) for v in self._vertices
        )

    @override
    def is_outside_bbox(self, entity_bbox: BoundingBox2d) -> bool:
        return not self.is_overlapping_bbox(entity_bbox)

    @override
    def is_overlapping_bbox(self, entity_bbox: BoundingBox2d) -> bool:
        if not self._bbox.has_overlap(entity_bbox):
            return False
        if any(
            is_point_in_polygon_2d(v, self._vertices) >= 0  # inside or on boundary
            for v in entity_bbox.rect_vertices()
        ):
            return True
        # special case: all bbox corners are outside the polygon but bbox edges may
        # intersect the polygon
        return self._has_intersection(entity_bbox.extmin, entity_bbox.extmax)


def bbox_inside(
    shape: SelectionShape,
    entities: Iterable[DXFEntity],
    *,
    cache: bbox.Cache | None = None,
) -> EntityQuery:
    """Selects entities whose bounding box lies withing the selection shape.

    Args:
        shape: seclection shape
        entities: iterable of DXFEntities
        cache: optional :class:`ezdxf.bbox.Cache` instance

    """
    return select_by_bbox(entities, shape.is_inside_bbox, cache)


def bbox_outside(
    shape: SelectionShape,
    entities: Iterable[DXFEntity],
    *,
    cache: bbox.Cache | None = None,
) -> EntityQuery:
    """Selects entities whose bounding box is completely outside the selection shape.

    Args:
        shape: seclection shape
        entities: iterable of DXFEntities
        cache: optional :class:`ezdxf.bbox.Cache` instance

    """
    return select_by_bbox(entities, shape.is_outside_bbox, cache)


def bbox_overlap(
    shape: SelectionShape,
    entities: Iterable[DXFEntity],
    *,
    cache: bbox.Cache | None = None,
) -> EntityQuery:
    """Selects entities whose bounding box overlaps the selection shape.

    Args:
        shape: seclection shape
        entities: iterable of DXFEntities
        cache: optional :class:`ezdxf.bbox.Cache` instance

    """
    return select_by_bbox(entities, shape.is_overlapping_bbox, cache)


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
        cache: optional :class:`ezdxf.bbox.Cache` instance

    """
    selection: list[DXFEntity] = []

    for entity in entities:
        extents = bbox.extents((entity,), fast=True, cache=cache)
        if not extents.has_data:
            continue
        if test_func(BoundingBox2d(extents)):
            selection.append(entity)
    return EntityQuery(selection)


def bbox_crosses_fence(
    vertices: Iterable[UVec],
    entities: Iterable[DXFEntity],
    *,
    cache: bbox.Cache | None = None,
) -> EntityQuery:
    """Selects entities whose bounding box intersects an open polyline.

    All entities are projected on the xy-plane.

    A single point can not be selected by a fence polyline by definition.

    Args:
        vertices: vertices of the selection polyline
        entities: iterable of DXFEntities
        cache: optional :class:`ezdxf.bbox.Cache` instance

    """

    def is_crossing(entity_bbox: BoundingBox2d) -> bool:
        if not _bbox.has_overlap(entity_bbox):
            return False
        if any(entity_bbox.inside(v) for v in _vertices):
            return True
        # All fence vertices are outside the entity bbox, but fence edges may
        # intersect the entity bbox.
        extmin = entity_bbox.extmin
        extmax = entity_bbox.extmax
        if extmin.isclose(extmax):  # is point
            return False  # by definition
        cs = CohenSutherlandLineClipping2d(extmin, extmax)
        return any(
            cs.clip_line(start, end) for start, end in zip(_vertices, _vertices[1:])
        )

    _vertices = Vec2.list(vertices)
    if len(_vertices) < 2:
        raise ValueError("2 or more vertices required")
    _bbox = BoundingBox2d(_vertices)

    return select_by_bbox(entities, is_crossing, cache)


def point_in_bbox(
    location: UVec, entities: Iterable[DXFEntity], *, cache: bbox.Cache | None = None
) -> EntityQuery:
    """Selects entities where the selection point lies within the bounding box.
    All entities are projected on the xy-plane.

    Args:
        point: selection point
        entities: iterable of DXFEntities
        cache: optional :class:`ezdxf.bbox.Cache` instance

    """

    def is_crossing(entity_bbox: BoundingBox2d) -> bool:
        return entity_bbox.inside(point)

    point = Vec2(location)
    return select_by_bbox(entities, is_crossing, cache)


def bbox_chained(
    start: DXFEntity, entities: Iterable[DXFEntity], *, cache: bbox.Cache | None = None
) -> EntityQuery:
    """Selects elements that are directly or indirectly connected to each other by
    overlapping bounding boxes. The selection begins at the specified starting element.

    Warning: the current implementation has a complexity of O(n²).

    Args:
        start: first entity of selection
        entities: iterable of DXFEntities
        cache: optional :class:`ezdxf.bbox.Cache` instance

    """

    def get_bbox_2d(entity: DXFEntity) -> BoundingBox2d:
        return BoundingBox2d(bbox.extents((entity,), fast=True, cache=cache))

    if cache is None:
        cache = bbox.Cache()
    selected: dict[DXFEntity, BoundingBox2d] = {start: get_bbox_2d(start)}

    entities = list(entities)
    restart = True
    while restart:
        restart = False
        for entity in entities:
            if entity in selected:
                continue
            entity_bbox = get_bbox_2d(entity)
            for selected_bbox in selected.values():
                if entity_bbox.has_overlap(selected_bbox):
                    selected[entity] = entity_bbox
                    restart = True
                    break

    return EntityQuery(selected.keys())
