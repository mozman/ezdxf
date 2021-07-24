#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, TYPE_CHECKING
from typing_extensions import Protocol, runtime_checkable
from ezdxf.query import EntityQuery

if TYPE_CHECKING:
    from ezdxf.entities import DXFGraphic


# Protocol implemented for:
# - DXFTagStorage
# - ACAD_PROXY_ENTITY
# - INSERT
#
# TODO:
#  - DIMENSION
#  - LEADER
#  - MLEADER
#  - MLINE
#  - POINT ???
#  - DXFGraphicProxy (drawing add-on)
#  - ProxyGraphic
#  - AbstractTrace (ezdxf.render.trace)
#  - TraceBuilder (ezdxf.render.trace)
#  - _Arrows (ezdxf.render.arrows)

@runtime_checkable
class SupportsVirtualEntities(Protocol):
    """ The virtual entities protocol is used to disassemble complex entities
    into DXF primitives like LINE, ARC, ... as REQUIREMENT to render these
    entities. Which means the entity does not have :func:`ezdxf.path.make_path`
    support, except the text entities TEXT, ATTRIB and MTEXT.

    Optional DECONSTRUCTION of entities into DXF primitives like LWPOLYLINE
    into LINE and ARC entities is NOT the intended usage of this protocol!

    This protocol is for consistent internal usage and does not replace
    the :meth:`virtual_entities` methods!

    """

    # The current state of the virtual_entities() method is a mixed usage of
    # these two use cases.
    #
    # Valid usage as REQUIREMENT:
    # INSERT
    # DIMENSION
    # ACAD_PROXY_ENTITY
    #
    # Misused for DECONSTRUCTION:
    # POLYLINE (2D, 3D, Mesh, Polyface)
    # LWPOLYLINE

    def __virtual_entities__(self) -> Iterable["DXFGraphic"]:
        ...


def virtual_entities(entity: SupportsVirtualEntities) -> Iterable["DXFGraphic"]:
    if isinstance(entity, SupportsVirtualEntities):
        return entity.__virtual_entities__()
    else:
        raise TypeError(
            f"{type(entity)!r} does not support the __virtual_entities__ protocol"
        )


def query_virtual_entities(entity: SupportsVirtualEntities) -> EntityQuery:
    return EntityQuery(virtual_entities(entity))
