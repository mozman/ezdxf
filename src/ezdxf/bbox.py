#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, Iterable, Dict, Optional
from ezdxf import disassemble
from ezdxf.math import BoundingBox, Vec3

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity

MAX_FLATTENING_DISTANCE = disassemble.Primitive.max_flattening_distance


class Cache:
    """ Caching object for :class:`ezdxf.math.BoundingBox` objects.

    Args:
        uuid: use UUIDs for virtual entities

    """

    def __init__(self, uuid=False):
        self._boxes: Dict[str, BoundingBox] = dict()
        self._use_uuid = bool(uuid)
        self.hits: int = 0
        self.misses: int = 0

    def __str__(self):
        return f"Cache(n={len(self._boxes)}, " \
               f"hits={self.hits}, " \
               f"misses={self.misses})"

    def get(self, entity: 'DXFEntity') -> Optional[BoundingBox]:
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

    def store(self, entity: 'DXFEntity', box: BoundingBox) -> None:
        assert entity is not None
        key = self._get_key(entity)
        if key is None:
            return
        self._boxes[key] = box

    def invalidate(self, entities: Iterable['DXFEntity']) -> None:
        """ Invalidate cache entries for the given DXF `entities`.

        If entities are changed by the user, it is possible to invalidate
        individual entities. Use with care - discarding the whole cache is
        the safer workflow.

        Ignores entities which are not stored in cache.

        """
        for entity in entities:
            try:
                del self._boxes[self._get_key(entity)]
            except KeyError:
                pass

    def _get_key(self, entity: 'DXFEntity') -> Optional[str]:
        if entity.dxftype() == 'HATCH':
            # Special treatment for multiple primitives for the same
            # HATCH entity - all have the same handle:
            # Do not store boundary path they are not distinguishable,
            # which boundary path should be returned for the handle?
            return None

        key = entity.dxf.handle
        if key is None or key == '0':
            return str(entity.uuid) if self._use_uuid else None
        else:
            return key


def multi_recursive(entities: Iterable['DXFEntity'], *,
                    flatten: float = MAX_FLATTENING_DISTANCE,
                    cache: Cache = None) -> Iterable[BoundingBox]:
    """ Yields all bounding boxes for the given `entities` **or** all bounding
    boxes for their sub entities. If an entity (INSERT) has sub entities, only
    the bounding boxes of these sub entities will be yielded, **not** the
    bounding box of entity (INSERT) itself.

    Calculate bounding boxes from flattened curves, if argument `flatten`
    is not 0 (max flattening distance), else from control points.

    """

    def vertices(p: disassemble.Primitive) -> Iterable[Vec3]:
        if flatten:
            primitive.max_flattening_distance = abs(flatten)
            return primitive.vertices()
        else:
            return disassemble.to_control_vertices([p])

    flat_entities = disassemble.recursive_decompose(entities)
    primitives = disassemble.to_primitives(flat_entities)
    for primitive in primitives:
        if primitive.is_empty:
            continue

        entity = primitive.entity
        if cache is not None:
            box = cache.get(entity)
            if box is None:
                box = BoundingBox(vertices(primitive))
                if box.has_data:
                    cache.store(entity, box)
        else:
            box = BoundingBox(vertices(primitive))

        if box.has_data:
            yield box


def extents(entities: Iterable['DXFEntity'], *,
            flatten: float = MAX_FLATTENING_DISTANCE,
            cache: Cache = None) -> BoundingBox:
    """ Returns a single bounding box for all given `entities`.

    Calculate bounding boxes from flattened curves, if argument `flatten`
    is not 0 (max flattening distance), else from control points.

    """
    _extends = BoundingBox()
    for box in multi_flat(entities, flatten=flatten, cache=cache):
        _extends.extend(box)
    return _extends


def multi_flat(entities: Iterable['DXFEntity'], *,
               flatten: float = MAX_FLATTENING_DISTANCE,
               cache: Cache = None) -> Iterable[BoundingBox]:
    """ Yields a bounding box for each of the given `entities`.

    Calculate bounding boxes from flattened curves, if argument `flatten`
    is not 0 (max flattening distance), else from control points.

    """

    def extends_(entities_: Iterable['DXFEntity']) -> BoundingBox:
        _extends = BoundingBox()
        for _box in multi_recursive(entities_, flatten=flatten, cache=cache):
            _extends.extend(_box)
        return _extends

    for entity in entities:
        box = None
        if cache:
            box = cache.get(entity)

        if box is None:
            box = extends_([entity])
            if cache:
                cache.store(entity, box)

        if box.has_data:
            yield box
