#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import TYPE_CHECKING, Iterable
from ezdxf import disassemble
from ezdxf.math import BoundingBox

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity


def multi_recursive(
        entities: Iterable['DXFEntity']) -> Iterable[BoundingBox]:
    """ Yields all bounding boxes for the given `entities` and all bounding
    boxes for their sub entities.

    """
    flat_entities = disassemble.recursive_decompose(entities)
    primitives = disassemble.to_primitives(flat_entities)
    for primitive in primitives:
        if not primitive.is_empty:
            box = BoundingBox(primitive.vertices())
            if box.has_data:
                yield box


def extends(entities: Iterable['DXFEntity']) -> BoundingBox:
    """ Returns a single bounding box for the given `entities` and their sub
    entities.

    """
    _extends = BoundingBox()
    for box in multi_recursive(entities):
        _extends.extend(box)
    return _extends


def multi_flat(entities: Iterable['DXFEntity']) -> Iterable[BoundingBox]:
    """ Yields all bounding boxes for the given `entities` at the top level,
    the sub entity extends are included, but they do not yield their own
    bounding boxes.

    """
    for entity in entities:
        box = extends([entity])
        if box.has_data:
            yield box
