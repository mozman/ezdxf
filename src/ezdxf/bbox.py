#  Copyright (c) 2021-2026, Manfred Moitzi
#  License: MIT License
"""Tools to calculate bounding boxes for many DXF entities.

The bounding box calculation is based on the :mod:`ezdxf.disassemble` module and
therefore has the same limitations. Unsupported DXF types like ACIS based
entities (BODY, 3DSOLID, REGION), external references (XREF), UNDERLAY, RAY,
XRAY and ACAD_TABLE are silently ignored. Bounding boxes of text entities are
not accurate, see :ref:`Text Boundary Calculation` for details.

The base type for all bounding boxes is the :class:`ezdxf.math.BoundingBox`
class. The `entities` argument of the functions in this module accepts any
iterable of DXF entities, e.g. the modelspace, an entity query or a list of
entities.

Use the optional :class:`ezdxf.bbox.Cache` class to speed up repeated
calculations of bounding boxes for nearly the same entity set.

"""
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable

from ezdxf import disassemble
from ezdxf.math import BoundingBox

if TYPE_CHECKING:
    from ezdxf.entities import DXFEntity

# Default max distance between the flattened approximation line and the original
# curve of the DXF primitives, see :class:`ezdxf.disassemble.Primitive`:
MAX_FLATTENING_DISTANCE = disassemble.Primitive.max_flattening_distance


class Cache:
    """Caching object for :class:`ezdxf.math.BoundingBox` objects.

    Building the DXF primitives of complex entities like block references is a
    time consuming task, therefore it is useful to cache the bounding boxes of
    entities which are processed multiple times.

    Entities are cached by their DXF handle. Entities without a handle - like
    virtual entities created on demand - are only cached if the `uuid` option
    is enabled, which caches them by their UUID. HATCH entities are never
    cached, because their boundary path primitives are not distinguishable by
    the HATCH handle.

    Args:
        uuid: use UUIDs for virtual entities without a handle

    Attributes:
        hits: count of cache hits
        misses: count of cache misses

    """

    def __init__(self, uuid=False) -> None:
        self._boxes: dict[str, BoundingBox] = dict()
        self._use_uuid = bool(uuid)
        self.hits: int = 0
        self.misses: int = 0

    @property
    def has_data(self) -> bool:
        """Returns ``True`` if the cache contains any bounding boxes."""
        return bool(self._boxes)

    def __str__(self):
        return (
            f"Cache(n={len(self._boxes)}, "
            f"hits={self.hits}, "
            f"misses={self.misses})"
        )

    def get(self, entity: DXFEntity) -> BoundingBox | None:
        """Returns the cached bounding box for `entity` or ``None`` if the
        entity is not cached.

        Increments the `hits` counter for cache hits and the `misses` counter
        otherwise. Entities which are not cacheable always count as a miss.

        Args:
            entity: DXF entity to look up

        """
        assert entity is not None
        key = self._get_key(entity)
        if key is None:
            self.misses += 1
            return None
        box = self._boxes.get(key)
        if box is None:
            self.misses += 1
        else:
            self.hits += 1
        return box

    def store(self, entity: DXFEntity, box: BoundingBox) -> None:
        """Store the bounding box `box` for `entity`.

        Replaces an already cached bounding box. The `hits` and `misses`
        counters are not affected.

        Args:
            entity: DXF entity
            box: bounding box of the entity

        """
        assert entity is not None
        key = self._get_key(entity)
        if key is None:
            return
        self._boxes[key] = box

    def invalidate(self, entities: Iterable[DXFEntity]) -> None:
        """Invalidate cache entries for the given DXF `entities`.

        If entities are changed by the user, it is possible to invalidate
        individual entities. Use with care - discarding the whole cache is
        the safer workflow.

        Ignores entities which are not stored in cache.

        Args:
            entities: iterable of DXF entities to invalidate

        """
        for entity in entities:
            try:
                del self._boxes[self._get_key(entity)]  # type: ignore
            except KeyError:
                pass

    def _get_key(self, entity: DXFEntity) -> str | None:
        """Returns the cache key for `entity` or ``None`` if the entity is not
        cacheable. (internal API)"""
        if entity.dxftype() == "HATCH":
            # Special treatment for multiple primitives for the same
            # HATCH entity - all have the same handle:
            # Do not store boundary path they are not distinguishable,
            # which boundary path should be returned for the handle?
            return None

        key = entity.dxf.handle
        if key is None or key == "0":
            return str(entity.uuid) if self._use_uuid else None
        else:
            return key


def multi_recursive(
    entities: Iterable[DXFEntity],
    *,
    fast=False,
    cache: Cache | None = None,
) -> Iterable[BoundingBox]:
    """Yields all bounding boxes for the given `entities` **or** all bounding
    boxes for their sub entities. If an entity (INSERT) has sub entities, only
    the bounding boxes of these sub entities will be yielded, **not** the
    bounding box of the entity (INSERT) itself.

    All entities are decomposed into DXF primitives first, therefore entities
    which are represented by more than one primitive - like HATCH - yield a
    bounding box for each primitive. Primitives without any vertices are
    ignored.

    Args:
        entities: iterable of DXF entities
        fast: calculate the bounding box of Bézier curves from their control
            points, this is faster but may return a slightly larger bounding
            box
        cache: optional :class:`Cache` object to speed up repeated
            calculations

    """
    flat_entities = disassemble.recursive_decompose(entities)
    primitives = disassemble.to_primitives(flat_entities)
    for primitive in primitives:
        if primitive.is_empty:
            continue

        entity = primitive.entity
        if cache is not None:
            box = cache.get(entity)
            if box is None:
                box = primitive.bbox(fast=fast)
                if box.has_data:
                    cache.store(entity, box)
        else:
            box = primitive.bbox(fast=fast)

        if box.has_data:
            yield box


def extents(
    entities: Iterable[DXFEntity],
    *,
    fast=False,
    cache: Cache | None = None,
) -> BoundingBox:
    """Returns a single bounding box for all given `entities`.

    The bounding box is calculated by :func:`multi_flat`, therefore complex
    entities like block references contribute a single bounding box for all
    their sub entities. Entities without a bounding box - like unsupported
    entities - are ignored. Returns an empty
    :class:`~ezdxf.math.BoundingBox` if no bounding box could be calculated.

    Args:
        entities: iterable of DXF entities
        fast: calculate the bounding box of Bézier curves from their control
            points, this is faster but may return a slightly larger bounding
            box
        cache: optional :class:`Cache` object to speed up repeated
            calculations

    Returns:
        the overall bounding box of all given entities

    """
    _extends = BoundingBox()
    for box in multi_flat(entities, fast=fast, cache=cache):
        _extends.extend(box)
    return _extends


def multi_flat(
    entities: Iterable[DXFEntity],
    *,
    fast=False,
    cache: Cache | None = None,
) -> Iterable[BoundingBox]:
    """Yields a single bounding box for each of the given `entities`.

    Entities with sub entities - like INSERT - are decomposed and the bounding
    boxes of all their sub entities are merged into one bounding box for the
    top level entity. LINE and POINT entities are handled directly without
    decomposition. Entities without a bounding box are ignored, therefore the
    count of yielded bounding boxes can be less than the count of the given
    entities.

    Args:
        entities: iterable of DXF entities
        fast: calculate the bounding box of Bézier curves from their control
            points, this is faster but may return a slightly larger bounding
            box
        cache: optional :class:`Cache` object to speed up repeated
            calculations

    Yields:
        bounding box of each entity which has a valid bounding box

    """

    def extends_(entities_: Iterable[DXFEntity]) -> BoundingBox:
        _extends = BoundingBox()
        for _box in multi_recursive(entities_, fast=fast, cache=cache):
            _extends.extend(_box)
        return _extends

    for entity in entities:
        box = None
        if cache:
            box = cache.get(entity)

        if box is None:
            dxftype = entity.dxftype()
            if dxftype == "LINE":
                box = BoundingBox((entity.dxf.start, entity.dxf.end))
            elif dxftype == "POINT":
                box = BoundingBox((entity.dxf.location,))
            else:
                box = extends_([entity])
            if cache:
                cache.store(entity, box)

        if box.has_data:
            yield box
