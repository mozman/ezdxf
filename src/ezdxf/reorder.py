# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Iterable, Tuple, Dict, Union

if TYPE_CHECKING:
    from ezdxf.eztypes import DXFEntity

__all__ = ['ascending', 'descending']


def ascending(entities: Iterable['DXFEntity'],
              mapping: Union[Dict, Iterable[Tuple[str, str]]] = None,
              ) -> Iterable['DXFEntity']:
    """ Yields entities in ascending handle order.

    The sort handle doesn't have to be the entity handle, every entity handle
    in `mapping` will be replaced by the given sort handle, `mapping` is an
    iterable of 2-tuples (entity_handle, sort_handle) or a
    dict[entity_handle, sort_handle]. Entities with equal sort handles show
    up in source entities order.

    Args:
        entities: iterable of :class:`DXFEntity` objects
        mapping: iterable of 2-tuples (entity_handle, sort_handle)

    """
    mapping = dict(mapping) if mapping else {}
    for _, _, entity in sorted(sort_structure(entities, mapping)):
        yield entity


def descending(entities: Iterable['DXFEntity'],
               mapping: Union[Dict, Iterable[Tuple[str, str]]] = None,
               ) -> Iterable['DXFEntity']:
    """ Yields entities in descending handle order.

    The sort handle doesn't have to be the entity handle, every entity handle
    in `mapping` will be replaced by the given sort handle, `mapping` is an
    iterable of 2-tuples (entity_handle, sort_handle) or a
    dict[entity_handle, sort_handle]. Entities with equal sort handles show
    up in reversed source entities order.

    Args:
        entities: iterable of :class:`DXFEntity` objects
        mapping: iterable of 2-tuples (entity_handle, sort_handle)

    """
    return reversed(list(ascending(entities, mapping)))


def sort_structure(entities: Iterable['DXFEntity'], mapping: Dict):
    def sort_handle(entity: 'DXFEntity') -> int:
        handle = entity.dxf.handle
        sort_handle_ = mapping.get(handle, handle)
        return int(sort_handle_, 16)
    # DXFEntity is not sortable, using the index as second order avoid using
    # a key function and preserves the source order of equal sort handles
    return [(sort_handle(entity), index, entity) for index, entity in enumerate(entities)]
