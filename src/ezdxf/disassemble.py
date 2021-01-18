#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, Optional, Tuple
from ezdxf.entities import DXFEntity
from ezdxf.math import Vec3
from ezdxf.render import Path, MeshBuilder, MeshVertexMerger, TraceBuilder

TPrimitives = Tuple[Optional[Path], Optional[MeshBuilder]]


def _default(e: DXFEntity) -> TPrimitives:
    return None, None


def _line(e: DXFEntity) -> TPrimitives:
    path = Path(e.dxf.start)
    path.line_to(e.dxf.end)
    return path, None


def _point(e: DXFEntity) -> TPrimitives:
    path = Path(e.dxf.location)
    return path, None


_CONVERTER = {
    "LINE": _line,
    "POINT": _point,
}


class Primitive:
    def __init__(self, entity: DXFEntity, flattening_distance: float = 0.1):
        self.flattening_distance = flattening_distance
        self.entity: Optional[DXFEntity] = entity
        # Path representation for linear entities:
        self.path: Optional[Path] = None
        # MeshBuilder representation for mesh based entities:
        # PolygonMesh, PolyFaceMesh, Mesh
        self.mesh: Optional[MeshBuilder] = None
        self._convert_entity(entity)

    def _convert_entity(self, entity: DXFEntity):
        converter = _CONVERTER.get(entity.dxftype(), _default)
        self.path, self.mesh = converter(entity)

    @property
    def is_path(self):
        return self.path is not None

    @property
    def is_mesh(self):
        return self.mesh is not None

    def vertices(self) -> Iterable[Vec3]:
        if self.is_path:
            if self.path:
                yield from self.path.flattening(self.flattening_distance)
            else:
                yield self.path.start
        elif self.is_mesh:
            yield from self.mesh.vertices
        else:
            return []


def recursive_decompose(entities: Iterable[DXFEntity]) -> Iterable[DXFEntity]:
    """ Recursive decompose the given DXF entity collection into a flat DXF
    entity stream. All block references (INSERT) will be disassembled into DXF
    entities, therefore the resulting entity stream does not contain any INSERT
    entity.

    """
    return []


def to_primitives(entities: Iterable[DXFEntity]) -> Iterable[Primitive]:
    """ Disassemble DXF entities into path/mesh primitive objects. """
    return (Primitive(e) for e in entities)


def to_vertices(primitives: Iterable[Primitive]) -> Iterable[Vec3]:
    """ Disassemble path/mesh primitive objects into vertices. """
    for p in primitives:
        yield from p.vertices()
