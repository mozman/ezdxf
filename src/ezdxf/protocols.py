#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, Iterator, Sequence, Iterable
from typing_extensions import Protocol, runtime_checkable
from ezdxf.query import EntityQuery

if TYPE_CHECKING:
    from ezdxf.entities import DXFGraphic, DXFEntity


# Protocol implemented for:
# - DXFTagStorage
# - ACAD_PROXY_ENTITY
# - INSERT
# - DIMENSION
# - LEADER
# - MLINE
# - ProxyGraphic
# - DXFGraphicProxy (drawing add-on)
#
# TODO: MLEADER, virtual_entities() not implemented yet


@runtime_checkable
class SupportsVirtualEntities(Protocol):
    """The virtual entities protocol is used to disassemble complex entities
    into DXF primitives like LINE, ARC, ... as REQUIREMENT to render these
    entities. Which means the entity does not have :func:`ezdxf.path.make_path`
    support, except the text entities TEXT, ATTRIB and MTEXT.

    Optional DECONSTRUCTION of entities into DXF primitives like LWPOLYLINE
    into LINE and ARC entities is NOT the intended usage of this protocol!

    This protocol is for consistent internal usage and does not replace
    the :meth:`virtual_entities` methods!

    """

    def __virtual_entities__(self) -> Iterator[DXFGraphic]:
        ...


def virtual_entities(entity: SupportsVirtualEntities) -> Iterator[DXFGraphic]:
    if isinstance(entity, SupportsVirtualEntities):
        return entity.__virtual_entities__()
    else:
        raise TypeError(
            f"{type(entity)!r} does not support the __virtual_entities__ protocol"
        )


def query_virtual_entities(entity: SupportsVirtualEntities) -> EntityQuery:
    return EntityQuery(virtual_entities(entity))


@runtime_checkable
class ReferencedBlocks(Protocol):
    def __referenced_blocks__(self) -> Iterable[str]:
        """Returns the handles to the BLOCK_RECORD entities for all BLOCK
        definitions used by an entity.
        """
        ...


_EMPTY_TUPLE: Tuple = tuple()


def referenced_blocks(entity: "DXFEntity") -> Iterable[str]:
    """Returns the handles to the BLOCK_RECORD entities for all BLOCK
    definitions used by an entity.
    """
    if isinstance(entity, ReferencedBlocks):
        return entity.__referenced_blocks__()
    else:
        return _EMPTY_TUPLE
