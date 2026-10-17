#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, Optional
from uuid import UUID

import ezdxf
from ezdxf import disassemble
from ezdxf.math import BoundingBox

if TYPE_CHECKING:
    from ezdxf.entities import DXFEntity

MAX_FLATTENING_DISTANCE = disassemble.Primitive.max_flattening_distance


class Cache:
    """Caching object for :class:`ezdxf.math.BoundingBox` objects.

    Precise and fast bounding boxes are stored separately. Entity UUIDs prevent
    collisions between equal handles from different documents and survive
    pickling together with the entities. The cache does not retain entities or
    documents. Changes to entities still require explicit invalidation.

    Args:
        uuid: use UUIDs for virtual entities

    """

    def __init__(self, uuid=False) -> None:
        self._boxes: dict[tuple[UUID, bool], BoundingBox] = dict()
        self._use_uuid = bool(uuid)
        self.hits: int = 0
        self.misses: int = 0

    @property
    def has_data(self) -> bool:
        return bool(self._boxes)

    def __str__(self):
        return (
            f"Cache(n={len(self._boxes)}, "
            f"hits={self.hits}, "
            f"misses={self.misses})"
        )

    def get(
        self, entity: DXFEntity, *, fast: Optional[bool] = None
    ) -> Optional[BoundingBox]:
        """Returns the cached box for the requested calculation mode.

        Omitting `fast` accepts either mode, preferring a precise box. This
        preserves the mode-independent lookup used by existing cache clients.
        """
        assert entity is not None
        key = self._get_key(entity)
        if key is None:
            self.misses += 1
            return None
        if fast is None:
            box = self._boxes.get((key, False))
            if box is None:
                box = self._boxes.get((key, True))
        else:
            box = self._boxes.get((key, bool(fast)))
        if box is None:
            self.misses += 1
        else:
            self.hits += 1
        return box

    def store(self, entity: DXFEntity, box: BoundingBox, *, fast=False) -> None:
        """Stores a box for the given calculation mode (precise by default)."""
        assert entity is not None
        key = self._get_key(entity)
        if key is None:
            return
        self._boxes[(key, bool(fast))] = box

    def invalidate(self, entities: Iterable[DXFEntity]) -> None:
        """Invalidate both calculation modes for the given DXF `entities`.

        If entities are changed by the user, it is possible to invalidate
        individual entities. Use with care - discarding the whole cache is
        the safer workflow.

        Ignores entities which are not stored in cache.

        """
        for entity in entities:
            key = self._get_key(entity)
            if key is not None:
                self._boxes.pop((key, False), None)
                self._boxes.pop((key, True), None)

    def _get_key(self, entity: DXFEntity) -> Optional[UUID]:
        if entity.dxftype() == "HATCH":
            # Special treatment for multiple primitives for the same
            # HATCH entity - all have the same handle:
            # Do not store boundary path they are not distinguishable,
            # which boundary path should be returned for the handle?
            return None

        if not self._use_uuid and entity.dxf.handle in (None, "0"):
            return None
        return entity.uuid


def multi_recursive(
    entities: Iterable[DXFEntity],
    *,
    fast=False,
    cache: Optional[Cache] = None,
) -> Iterable[BoundingBox]:
    """Yields all bounding boxes for the given `entities` **or** all bounding
    boxes for their sub entities. If an entity (INSERT) has sub entities, only
    the bounding boxes of these sub entities will be yielded, **not** the
    bounding box of the entity (INSERT) itself.

    If argument `fast` is ``True`` the calculation of Bézier curves is based on
    their control points, this may return a slightly larger bounding box.

    """
    flat_entities = disassemble.recursive_decompose(entities)
    primitives = disassemble.to_primitives(flat_entities)
    for primitive in primitives:
        if primitive.is_empty:
            continue

        entity = primitive.entity
        if cache is not None:
            box = cache.get(entity, fast=fast)
            if box is None:
                box = primitive.bbox(fast=fast)
                if box.has_data:
                    cache.store(entity, box, fast=fast)
        else:
            box = primitive.bbox(fast=fast)

        if box.has_data:
            yield box


def extents(
    entities: Iterable[DXFEntity],
    *,
    fast=False,
    cache: Optional[Cache] = None,
) -> BoundingBox:
    """Returns a single bounding box for all given `entities`.

    If argument `fast` is ``True`` the calculation of Bézier curves is based on
    their control points, this may return a slightly larger bounding box.

    """
    _extends = BoundingBox()
    for box in multi_flat(entities, fast=fast, cache=cache):
        _extends.extend(box)
    return _extends


def multi_flat(
    entities: Iterable[DXFEntity],
    *,
    fast=False,
    cache: Optional[Cache] = None,
) -> Iterable[BoundingBox]:
    """Yields a bounding box for each of the given `entities`.

    If argument `fast` is ``True`` the calculation of Bézier curves is based on
    their control points, this may return a slightly larger bounding box.

    """

    def extends_(entities_: Iterable[DXFEntity]) -> BoundingBox:
        _extends = BoundingBox()
        for _box in multi_recursive(entities_, fast=fast, cache=cache):
            _extends.extend(_box)
        return _extends

    for entity in entities:
        box = None
        if cache:
            box = cache.get(entity, fast=fast)

        if box is None:
            dxftype = entity.dxftype()
            if dxftype == "LINE":
                box = BoundingBox((entity.dxf.start, entity.dxf.end))
            elif dxftype == "POINT":
                box = BoundingBox((entity.dxf.location,))
            else:
                box = extends_([entity])
            if cache:
                cache.store(entity, box, fast=fast)

        if box.has_data:
            yield box
