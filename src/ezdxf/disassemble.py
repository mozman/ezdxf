#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, Optional, cast, TYPE_CHECKING
import abc
import math
from ezdxf.entities import DXFEntity
from ezdxf.lldxf import const
from ezdxf.math import Vec3, Matrix44
from ezdxf.render import (
    Path, MeshBuilder, MeshVertexMerger, TraceBuilder, make_path, forms,
)

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        LWPolyline, Polyline,
    )


class AbstractPrimitive:
    """ It is not efficient to create the Path() or MeshBuilder() representation
    by default. For some entities the it's just not needed (LINE, POINT) and for
    others the builtin flattening() method is more efficient or accurate than
    using a Path() proxy object. (ARC, CIRCLE, ELLIPSE, SPLINE).

    The `max_flattening_distance` defines the max distance between the
    approximation line and the original curve. Use argument
    `max_flattening_distance` to override the default value, or set the value
    by direct attribute access.

    """
    max_flattening_distance: float = 0.01

    def __init__(self, entity: DXFEntity, max_flattening_distance=None):
        self.entity: DXFEntity = entity
        # Path representation for linear entities:
        self._path: Optional[Path] = None
        # MeshBuilder representation for mesh based entities:
        # PolygonMesh, PolyFaceMesh, Mesh
        self._mesh: Optional[MeshBuilder] = None
        if max_flattening_distance:
            self.max_flattening_distance = max_flattening_distance

    @property
    def path(self) -> Optional[Path]:
        """ :class:`~ezdxf.render.path.Path` representation or ``None``,
        idiom to check if is a path representation (could be empty)::

            if primitive.path is not None:
                process(primitive.path)

        """
        return None

    @property
    def mesh(self) -> Optional[MeshBuilder]:
        """ :class:`~ezdxf.render.mesh.MeshBuilder` representation or ``None``,
        idiom to check if is a mesh representation (could be empty)::

            if primitive.mesh is not None:
                process(primitive.mesh)

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
            yield from self._path.flattening(self.max_flattening_distance)
        elif self.mesh:
            yield from self._mesh.vertices


class CurvePrimitive(AbstractPrimitive):
    @property
    def path(self) -> Optional[Path]:
        """ Create path representation on demand. """
        if self._path is None:
            self._path = make_path(self.entity)
        return self._path

    def vertices(self) -> Iterable[Vec3]:
        # Not faster but more precise, because cubic bezier curves do not
        # perfectly represent elliptic arcs (CIRCLE, ARC, ELLIPSE).
        # SPLINE: cubic bezier curves do not perfectly represent splines with
        # degree != 3.
        yield from self.entity.flattening(self.max_flattening_distance)


class LinePrimitive(AbstractPrimitive):
    @property
    def path(self) -> Optional[Path]:
        """ Create path representation on demand. """
        if self._path is None:
            self._path = make_path(self.entity)
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
            self._path = make_path(e)


class PointPrimitive(AbstractPrimitive):
    @property
    def path(self) -> Optional[Path]:
        """ Create path representation on demand.

        :class:`Path` can not represent a point, a :class:`Path` with only a
        start point yields not vertices!

        """
        if self._path is None:
            self._path = Path(self.entity.dxf.location)
        return self._path

    def vertices(self) -> Iterable[Vec3]:
        yield self.entity.dxf.location


class MeshPrimitive(GenericPrimitive):
    def _convert_entity(self):
        self._mesh = MeshBuilder.from_mesh(self.entity)


class QuadrilateralPrimitive(GenericPrimitive):
    def _convert_entity(self):
        self._path = make_path(self.entity)


class PolylinePrimitive(GenericPrimitive):
    def _convert_entity(self):
        e: 'Polyline' = cast('Polyline', self.entity)
        if e.is_2d_polyline or e.is_3d_polyline:
            self._path = make_path(e)
        else:
            m = MeshVertexMerger.from_polyface(e)
            self._mesh = MeshBuilder.from_builder(m)


DESCENDERS_FACTOR = 0.333  # from TXT SHX font - just guessing


class TextLinePrimitive(GenericPrimitive):
    def _convert_entity(self):
        """ Creates a rough bounding box for a single line text.

        Calculation is based on a mono-spaced font and therefore the bounding
        box is just an educated guess.

        """

        def get_text_rotation():
            if alignment in ('FIT', 'ALIGNED') and not p1.isclose(p2):
                return (p2 - p1).angle
            else:
                return math.degrees(text.dxf.rotation)

        def get_insert():
            if alignment == 'LEFT':
                return p1
            elif alignment in ('FIT', 'ALIGNED'):
                return p1.lerp(p2, factor=0.5)
            else:
                return p2

        def text_stretch_factor():
            sx = 1.0
            sy = 1.0
            if alignment in ('FIT', 'ALIGNED'):
                defined_length = (p2 - p1).magnitude
                if text_width > 1e-9:
                    sx = defined_length / text_width
                    if alignment == "ALIGNED":
                        sy = sx
            return sx, sy

        def shift_x() -> float:
            if halign == const.CENTER:
                return -total_width / 2.0
            elif halign == const.RIGHT:
                return -total_width
            return 0.0  # LEFT

        def shift_y():
            if valign == const.BASELINE:
                return -total_descenders_height
            elif valign == const.MIDDLE:
                return -total_cap_height / 2.0 - total_descenders_height
            elif valign == const.TOP:
                return -total_height
            return 0.0  # BOTTOM

        text = cast('Text', self.entity)
        char_count = len(text.dxf.text)
        if char_count == 0:
            # empty path - does not render any vertices!
            self._path = Path()
            return

        p1 = text.dxf.insert
        p2 = text.dxf.align_point
        halign = text.dxf.halign
        valign = text.dxf.valign
        alignment = text.get_align()
        if alignment == 'MIDDLE':  # valign is stored as BASELINE
            valign = const.MIDDLE
        if alignment in ('MIDDLE', 'FIT', 'ALIGNED'):
            halign = const.CENTER

        # Text height of an uppercase letter without descenders:
        text_height = text.dxf.height

        width_factor = text.dxf.width
        text_width = char_count * text_height * width_factor
        sx, sy = text_stretch_factor()
        total_width = text_width * sx

        # https://www.fonts.com/content/learning/fontology/level-1/type-anatomy/anatomy
        total_cap_height = text_height * sy
        total_descenders_height = total_cap_height * DESCENDERS_FACTOR
        total_height = total_cap_height + total_descenders_height

        bbox_vertices = forms.box(total_width, total_height)
        insert = get_insert()
        m = Matrix44.chain(
            Matrix44.translate(  # to rotation center
                shift_x(),
                shift_y(),
                0,  # ignore z-axis = OCS elevation
            ),
            Matrix44.z_rotate(get_text_rotation()),
            Matrix44.translate(
                insert.x,
                insert.y,
                0,  # ignore z-axis = OCS elevation
            ),
        )
        # TODO: text generation flags?
        ocs = text.ocs()
        bbox = Path.from_vertices(
            ocs.points_to_wcs(m.transform_vertices(bbox_vertices)),
            close=True,
        )
        self._path = bbox


_PRIMITIVE_CLASSES = {
    "3DFACE": QuadrilateralPrimitive,
    "ARC": CurvePrimitive,
    "ATTRIB": TextLinePrimitive,
    "ATTDEF": TextLinePrimitive,
    "CIRCLE": CurvePrimitive,
    "ELLIPSE": CurvePrimitive,
    "HELIX": CurvePrimitive,
    "LINE": LinePrimitive,
    "LWPOLYLINE": LwPolylinePrimitive,
    "MESH": MeshPrimitive,
    "POINT": PointPrimitive,
    "POLYLINE": PolylinePrimitive,
    "SPLINE": CurvePrimitive,
    "SOLID": QuadrilateralPrimitive,
    "TEXT": TextLinePrimitive,
    "TRACE": QuadrilateralPrimitive,
}


def make_primitive(e: DXFEntity,
                   max_flattening_distance=None) -> AbstractPrimitive:
    """ Factory to create path/mesh primitives. The `max_flattening_distance`
    defines the max distance between the approximation line and the original
    curve. Use `max_flattening_distance` to override the default value.

    Returns an empty primitive for unsupported entities, where the :attr:`path`
    and the :attr:`mesh` attribute is ``None`` and the :meth:`vertices` method
    yields an empty list of vertices.

    """
    cls = _PRIMITIVE_CLASSES.get(e.dxftype(), GenericPrimitive)
    primitive = cls(e)
    if max_flattening_distance:
        primitive.max_flattening_distance = max_flattening_distance
    return primitive


def recursive_decompose(entities: Iterable[DXFEntity]) -> Iterable[DXFEntity]:
    """ Recursive decompose the given DXF entity collection into a flat DXF
    entity stream. All block references (INSERT) will be disassembled into DXF
    entities, therefore the resulting entity stream does not contain any INSERT
    entity.

    """
    return []


def to_primitives(entities: Iterable[DXFEntity],
                  max_flattening_distance=None) -> Iterable[AbstractPrimitive]:
    """ Disassemble DXF entities into path/mesh primitive objects. Yields
    unsupported entities as empty primitives, see :func:`make_primitive`.
    """
    return (make_primitive(e, max_flattening_distance) for e in entities)


def to_vertices(primitives: Iterable[AbstractPrimitive]) -> Iterable[Vec3]:
    """ Disassemble path/mesh primitive objects into vertices. """
    for p in primitives:
        yield from p.vertices()
