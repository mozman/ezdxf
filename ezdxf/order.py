# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# created: 2019-02-16
from typing import Iterable, Callable

__all__ = ['priority', 'zorder']


def priority_key(item) -> int:
    try:
        return item.priority
    except AttributeError:
        return 0


def priority(items: Iterable, key: Callable = None) -> Iterable:
    """ Iterate over all entities in priority (highest priority first).

    Highest priority first means: 10, 5, 5, 0, 0, 0, -1, -99

    Reason is to use the priority in two ways:

    1. set order of appearance in for objects section, highest priority for the root dict, which must be the first
       entity in the objects section, an down counting iterator (highest priority first) is intuitive.

    2. define entity appearance in the entities section, first entity in the entities section is the lowest by
       z-order, so an up counting iterator (highest priority at last) is more intuitive.

    """
    return iter(sorted(items, key=key or priority_key, reverse=True))


def zorder(items: Iterable, key: Callable = None) -> Iterable:
    """ Iterate over all entities in z-order (lowest priority first).

    Lowest priority first means: -99, -1, 0, 0, 0, 5, 5, 10

    Reason is to use the priority in two ways:

    1. set order of appearance in for objects section, highest priority for the root dict, which must be the first
       entity in the objects section, an down counting iterator (highest priority first) is intuitive.

    2. define entity appearance in the entities section, first entity in the entities section is the lowest by
       z-order, so an up counting iterator (highest priority at last) is more intuitive.

    """
    return iter(sorted(items, key=key or priority_key))
