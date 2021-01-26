#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, Iterable, Dict, Optional
from ezdxf import disassemble
from ezdxf.math import BoundingBox

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity


class Cache:
    def __init__(self):
        self._boxes: Dict[str, BoundingBox] = dict()
        self.hits: int = 0
        self.misses: int = 0

    def get(self, entity: 'DXFEntity') -> Optional[BoundingBox]:
        assert entity is not None
        handle = entity.dxf.handle
        if handle is None or handle == '0':
            self.misses += 1
            return None
        box = self._boxes.get(handle)
        if box is None:
            self.misses += 1
        else:
            self.hits += 1
        return box

    def store(self, entity: 'DXFEntity', box: BoundingBox) -> None:
        assert entity is not None
        handle = entity.dxf.handle
        if handle is None or handle == '0':
            return
        if entity.dxftype() == 'HATCH':
            # Special treatment for multiple primitives for the same
            # HATCH entity - all have the same handle:
            # Do not store boundary path they are not distinguishable,
            # which boundary path should be returned for the handle?
            return
        self._boxes[handle] = box


def multi_recursive(
        entities: Iterable['DXFEntity'],
        cache: Cache = None) -> Iterable[BoundingBox]:
    """ Yields all bounding boxes for the given `entities` and all bounding
    boxes for their sub entities.

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
                box = BoundingBox(primitive.vertices())
                if box.has_data:
                    cache.store(entity, box)
        else:
            box = BoundingBox(primitive.vertices())

        if box.has_data:
            yield box


def extends(entities: Iterable['DXFEntity'],
            cache: Cache = None) -> BoundingBox:
    """ Returns a single bounding box for the given `entities` and their sub
    entities.

    """
    _extends = BoundingBox()
    for box in multi_recursive(entities, cache):
        _extends.extend(box)
    return _extends


def multi_flat(entities: Iterable['DXFEntity'],
               cache: Cache = None) -> Iterable[BoundingBox]:
    """ Yields all bounding boxes for the given `entities` at the top level,
    the sub entity extends are included, but they do not yield their own
    bounding boxes.

    """
    for entity in entities:
        box = extends([entity], cache)
        if box.has_data:
            yield box
