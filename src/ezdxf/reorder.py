# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Tuple, Dict, Union

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFGraphic

__all__ = ['ascending', 'descending']


def ascending(entities: Iterable['DXFGraphic'],
              mapping: Union[Dict, Iterable[Tuple[str, str]]] = None,
              ) -> Iterable['DXFGraphic']:
    """ Yields entities in ascending handle order.

    The sort handle doesn't have to be the entity handle, every entity handle
    in `mapping` will be replaced by the given sort handle, `mapping` is an
    iterable of 2-tuples (entity_handle, sort_handle) or a
    dict[entity_handle, sort_handle]. Entities with equal sort handles show
    up in source entities order.

    Args:
        entities: iterable of :class:`DXFGraphic` objects
        mapping: iterable of 2-tuples (entity_handle, sort_handle)

    """
    mapping = dict(mapping) if mapping else {}
    # Entities with sort handle "0" will be draw at last - so defined by AutoCAD
    at_last = []
    for sort_handle, _, entity in sorted(sort_structure(entities, mapping)):
        if sort_handle == 0:
            at_last.append(entity)
        else:
            yield entity
    yield from at_last


def descending(entities: Iterable['DXFGraphic'],
               mapping: Union[Dict, Iterable[Tuple[str, str]]] = None,
               ) -> Iterable['DXFGraphic']:
    """ Yields entities in descending handle order.

    The sort handle doesn't have to be the entity handle, every entity handle
    in `mapping` will be replaced by the given sort handle, `mapping` is an
    iterable of 2-tuples (entity_handle, sort_handle) or a
    dict[entity_handle, sort_handle]. Entities with equal sort handles show
    up in reversed source entities order.

    Args:
        entities: iterable of :class:`DXFGraphic` objects
        mapping: iterable of 2-tuples (entity_handle, sort_handle)

    """
    return reversed(list(ascending(entities, mapping)))


def sort_structure(entities: Iterable['DXFGraphic'], mapping: Dict):
    def sort_handle(entity: 'DXFGraphic') -> int:
        handle = entity.dxf.handle
        sort_handle_ = mapping.get(handle, handle)
        return int(sort_handle_, 16)
    # DXFGraphic is not sortable, using the index as second value avoids a key
    # function and preserves explicit the source order of equal sort handles.
    return [(sort_handle(entity), index, entity) for index, entity in enumerate(entities)]
