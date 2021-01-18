#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, Optional, Tuple, cast, TYPE_CHECKING
import abc
from ezdxf.entities import DXFEntity
from ezdxf.math import Vec3
from ezdxf.render import Path, MeshBuilder, MeshVertexMerger, TraceBuilder

if TYPE_CHECKING:
    from ezdxf.eztypes import LWPolyline


class AbstractPrimitive:
    """ It is not efficient to create the Path() or MeshBuilder() representation
    by default. For some entities the it's just not needed (LINE, POINT) and for
    others the builtin flattening() method is more efficient or accurate than
    using a Path() proxy object. (ARC, CIRCLE, ELLIPSE, SPLINE).

    """
    flattening_distance: float = 0.1

    def __init__(self, entity: DXFEntity):
        self.entity: DXFEntity = entity
        # Path representation for linear entities:
        self._path: Optional[Path] = None
        # MeshBuilder representation for mesh based entities:
        # PolygonMesh, PolyFaceMesh, Mesh
        self._mesh: Optional[MeshBuilder] = None

    @property
    def path(self) -> Optional[Path]:
        """ :class:`~ezdxf.render.path.Path` representation or ``None`` """
        return None

    @property
    def mesh(self) -> Optional[MeshBuilder]:
        """ :class:`~ezdxf.render.mesh.MeshBuilder` representation or ``None``
        """
        return None

    @abc.abstractmethod
    def vertices(self) -> Iterable[Vec3]:
        """ Yields all vertices of the path/mesh representation as
        :class:`~ezdxf.math.Vec3` objects.

        """
        pass


class GenericPrimitive(AbstractPrimitive):
    """ Base class for all DXF entities which store the path/mesh representation
    at instantiation.

    """

    def __init__(self, entity: DXFEntity):
        super().__init__(entity)
        self._convert_entity()

    def _convert_entity(self):
        """ This method creates the path/mesh representation. """
        pass

    @property
    def path(self) -> Optional[Path]:
        return self._path

    @property
    def mesh(self) -> Optional[MeshBuilder]:
        return self._mesh

    def vertices(self) -> Iterable[Vec3]:
        if self.path:
            yield from self._path.flattening(self.flattening_distance)
        elif self.mesh:
            yield from self._mesh.vertices


class PointPrimitive(AbstractPrimitive):
    @property
    def path(self) -> Optional[Path]:
        """ Create path representation on demand. """
        if self._path is None:
            self._path = Path(self.entity.dxf.location)
        return self._path

    def vertices(self) -> Iterable[Vec3]:
        yield self.entity.dxf.location


class LinePrimitive(AbstractPrimitive):
    @property
    def path(self) -> Optional[Path]:
        """ Create path representation on demand. """
        if self._path is None:
            e = self.entity
            self._path = Path(e.dxf.start)
            self._path.line_to(e.dxf.end)
        return self._path

    def vertices(self) -> Iterable[Vec3]:
        e = self.entity
        yield e.dxf.start
        yield e.dxf.end


class LwPolylinePrimitive(GenericPrimitive):
    def _convert_entity(self):
        e: 'LWPolyline' = cast('LWPolyline', self.entity)
        if e.has_width:  # use a mesh representation:
            tb = TraceBuilder.from_polyline(e)
            mb = MeshVertexMerger()  # merges coincident vertices
            for face in tb.faces():
                mb.add_face(face)
            self._mesh = MeshBuilder.from_builder(mb)
        else:  # use a path representation to support bulges!
            self._path = Path.from_lwpolyline(e)


_PRIMITIVE_CLASSES = {
    "LINE": LinePrimitive,
    "POINT": PointPrimitive,
    "LWPOLYLINE": LwPolylinePrimitive,
}


def make_primitive(e: DXFEntity) -> AbstractPrimitive:
    """ Factory to create path/mesh primitives. """
    cls = _PRIMITIVE_CLASSES.get(e.dxftype(), GenericPrimitive)
    return cls(e)


def recursive_decompose(entities: Iterable[DXFEntity]) -> Iterable[DXFEntity]:
    """ Recursive decompose the given DXF entity collection into a flat DXF
    entity stream. All block references (INSERT) will be disassembled into DXF
    entities, therefore the resulting entity stream does not contain any INSERT
    entity.

    """
    return []


def to_primitives(entities: Iterable[DXFEntity]) -> Iterable[AbstractPrimitive]:
    """ Disassemble DXF entities into path/mesh primitive objects. """
    return (make_primitive(e) for e in entities)


def to_vertices(primitives: Iterable[AbstractPrimitive]) -> Iterable[Vec3]:
    """ Disassemble path/mesh primitive objects into vertices. """
    for p in primitives:
        yield from p.vertices()
