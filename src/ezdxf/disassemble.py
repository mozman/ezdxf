#  Copyright (c) 2021, Manfred Moitzi
#  License: MIT License
from typing import Iterable, Optional, cast, TYPE_CHECKING, List
import abc
import math
from ezdxf.entities import DXFEntity
from ezdxf.lldxf import const
from ezdxf.math import Vec3, UCS, Z_AXIS, X_AXIS
from ezdxf.render import (
    Path, MeshBuilder, MeshVertexMerger, TraceBuilder, make_path,
)
from ezdxf.proxygraphic import ProxyGraphic
from ezdxf.tools.text import (
    TextLine, unified_alignment, plain_text, text_wrap
)
from ezdxf.tools import fonts

if TYPE_CHECKING:
    from ezdxf.eztypes import LWPolyline, Polyline, MText, Hatch, Insert

__all__ = [
    "make_primitive", "recursive_decompose", "to_primitives", "to_vertices"
]


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
    def is_empty(self) -> bool:
        """ Returns `True` if represents an empty primitive which do not
        yield any vertices.

        """
        if self._mesh:
            return len(self._mesh.vertices) == 0
        return self.path is None  # on demand calculations!

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
                mb.add_face(Vec3.generate(face))
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


DESCENDER_FACTOR = 0.333  # from TXT SHX font - just guessing
X_HEIGHT_FACTOR = 0.666  # from TXT SHX font - just guessing


def get_font_name(entity: 'DXFEntity'):
    font_name = "txt"
    if entity.doc:
        style_name = entity.dxf.style
        style = entity.doc.styles.get(style_name)
        if style:
            font_name = style.dxf.font
    return font_name


class TextLinePrimitive(GenericPrimitive):
    def _convert_entity(self):
        """ Calculates the rough border path for a single line text.

        Calculation is based on a mono-spaced font and therefore the border
        path is just an educated guess.

        Vertical text generation and oblique angle is ignored.

        """

        def get_text_rotation() -> float:
            if alignment in ('FIT', 'ALIGNED') and not p1.isclose(p2):
                return (p2 - p1).angle
            else:
                return math.degrees(text.dxf.rotation)

        def get_insert() -> Vec3:
            if alignment == 'LEFT':
                return p1
            elif alignment in ('FIT', 'ALIGNED'):
                return p1.lerp(p2, factor=0.5)
            else:
                return p2

        text = cast('Text', self.entity)
        if text.dxftype() == 'ATTDEF':
            # ATTDEF outside of a BLOCK renders the tag rather than the value
            content = text.dxf.tag
        else:
            content = text.dxf.text

        content = plain_text(content)
        if len(content) == 0:
            # empty path - does not render any vertices!
            self._path = Path()
            return

        p1: Vec3 = text.dxf.insert
        p2: Vec3 = text.dxf.align_point
        font = fonts.make_font(get_font_name(text), text.dxf.height, text.dxf.width)
        text_line = TextLine(content, font)
        alignment: str = text.get_align()
        if text.dxf.halign > 2:  # ALIGNED=3, MIDDLE=4, FIT=5
            text_line.stretch(alignment, p1, p2)
        halign, valign = unified_alignment(text)
        corner_vertices = text_line.corner_vertices(
            get_insert(), halign, valign, get_text_rotation())

        ocs = text.ocs()
        self._path = Path.from_vertices(
            ocs.points_to_wcs(corner_vertices),
            close=True,
        )


class MTextPrimitive(GenericPrimitive):
    def _convert_entity(self):
        """ Calculates the rough border path for a MTEXT entity.

        Calculation is based on a mono-spaced font and therefore the border
        path is just an educated guess.

        Most special features of MTEXT is not supported.

        """

        def get_content() -> List[str]:
            text = mtext.plain_text(split=False)
            return text_wrap(text, box_width, font.text_width)

        def get_max_str() -> str:
            return max(content, key=lambda s: len(s))

        def get_rect_width() -> float:
            if box_width:
                return box_width
            s = get_max_str()
            if len(s) == 0:
                s = " "
            return font.text_width(s)

        def get_rect_height() -> float:
            line_height = font.measurements.total_height
            cap_height = font.measurements.cap_height
            # Line spacing factor: Percentage of default (3-on-5) line
            # spacing to be applied.

            # thx to mbway: multiple of cap_height between the baseline of the
            # previous line and the baseline of the next line
            # 3-on-5 line spacing = 5/3 = 1.67
            line_spacing = cap_height * mtext.dxf.line_spacing_factor * 1.67
            spacing = line_spacing - line_height
            line_count = len(content)
            return line_height * line_count + spacing * (line_count - 1)

        def get_ucs() -> UCS:
            """ Create local coordinate system:
            origin = insertion point
            z-axis = extrusion vector
            x-axis = text_direction or text rotation, text rotation requires
                extrusion vector == (0, 0, 1) or treatment like an OCS?

            """
            origin = mtext.dxf.insert
            z_axis = mtext.dxf.extrusion  # default is Z_AXIS
            x_axis = X_AXIS
            if mtext.dxf.hasattr('text_direction'):
                x_axis = mtext.dxf.text_direction
            elif mtext.dxf.hasattr('rotation'):
                # TODO: what if extrusion vector is not (0, 0, 1)
                x_axis = Vec3.from_deg_angle(mtext.dxf.rotation)
                z_axis = Z_AXIS
            return UCS(origin=origin, ux=x_axis, uz=z_axis)

        def get_shift_factors():
            halign, valign = unified_alignment(mtext)
            shift_x = 0
            shift_y = 0
            if halign == const.CENTER:
                shift_x = -0.5
            elif halign == const.RIGHT:
                shift_x = -1.0
            if valign == const.MIDDLE:
                shift_y = 0.5
            elif valign == const.BOTTOM:
                shift_y = 1.0
            return shift_x, shift_y

        def get_corner_vertices() -> Iterable[Vec3]:
            """ Create corner vertices in the local working plan, where
            the insertion point is the origin.
            """
            rect_width = mtext.dxf.get('rect_width', get_rect_width())
            rect_height = mtext.dxf.get('rect_height', get_rect_height())
            # TOP LEFT alignment:
            vertices = [
                Vec3(0, 0),
                Vec3(rect_width, 0),
                Vec3(rect_width, -rect_height),
                Vec3(0, -rect_height)
            ]
            sx, sy = get_shift_factors()
            shift = Vec3(sx * rect_width, sy * rect_height)
            return (v + shift for v in vertices)

        mtext: "MText" = cast("MText", self.entity)
        box_width = mtext.dxf.get('width', 0)
        font = fonts.make_font(get_font_name(mtext), mtext.dxf.char_height, 1.0)

        content: List[str] = get_content()
        if len(content) == 0:
            # empty path - does not render any vertices!
            self._path = Path()
            return
        ucs = get_ucs()
        corner_vertices = get_corner_vertices()
        self._path = Path.from_vertices(
            ucs.points_to_wcs(corner_vertices),
            close=True,
        )


class PathPrimitive(AbstractPrimitive):
    def __init__(self, path: Path, entity: DXFEntity,
                 max_flattening_distance=None):
        super().__init__(entity, max_flattening_distance)
        self._path = path

    def vertices(self) -> Iterable[Vec3]:
        yield from self._path.flattening(self.max_flattening_distance)


class ImagePrimitive(GenericPrimitive):
    def _convert_entity(self):
        self._path = make_path(self.entity)


class ViewportPrimitive(GenericPrimitive):
    def _convert_entity(self):
        vp = self.entity
        if vp.dxf.status == 0:  # Viewport is off
            return  # empty primitive
        self._path = make_path(vp)


# SHAPE is not supported, could not create any SHAPE entities in BricsCAD
_PRIMITIVE_CLASSES = {
    "3DFACE": QuadrilateralPrimitive,
    "ARC": CurvePrimitive,
    # TODO: ATTRIB and ATTDEF could contain embedded MTEXT,
    #  but this is not supported yet!
    "ATTRIB": TextLinePrimitive,
    "ATTDEF": TextLinePrimitive,
    "CIRCLE": CurvePrimitive,
    "ELLIPSE": CurvePrimitive,
    # HATCH: Special handling required, see to_primitives() function
    "HELIX": CurvePrimitive,
    "IMAGE": ImagePrimitive,
    "LINE": LinePrimitive,
    "LWPOLYLINE": LwPolylinePrimitive,
    "MESH": MeshPrimitive,
    "MTEXT": MTextPrimitive,
    "POINT": PointPrimitive,
    "POLYLINE": PolylinePrimitive,
    "SPLINE": CurvePrimitive,
    "SOLID": QuadrilateralPrimitive,
    "TEXT": TextLinePrimitive,
    "TRACE": QuadrilateralPrimitive,
    "VIEWPORT": ViewportPrimitive,
    "WIPEOUT": ImagePrimitive,
}


def make_primitive(e: DXFEntity,
                   max_flattening_distance=None) -> AbstractPrimitive:
    """ Factory to create path/mesh primitives. The `max_flattening_distance`
    defines the max distance between the approximation line and the original
    curve. Use `max_flattening_distance` to override the default value.

    Returns an empty primitive for unsupported entities, can be checked by
    property :attr:`is_empty`. The :attr:`path` and the :attr:`mesh` attribute
    is ``None`` and the :meth:`vertices` method yields no vertices.

    Returns an empty primitive for the :class:`~ezdxf.entities.Hatch` entity,
    see docs of the :mod:`~ezdxf.disassemble` module.

    """
    cls = _PRIMITIVE_CLASSES.get(e.dxftype(), GenericPrimitive)
    primitive = cls(e)
    if max_flattening_distance:
        primitive.max_flattening_distance = max_flattening_distance
    return primitive


def recursive_decompose(entities: Iterable[DXFEntity]) -> Iterable[DXFEntity]:
    """ Recursive decomposition of the given DXF entity collection into a flat
    DXF entity stream. All block references (INSERT) and entities which provide
    a :meth:`virtual_entities` method will be disassembled into simple DXF
    sub-entities, therefore the returned entity stream does not contain any
    INSERT entity.

    Point entities will **not** be disassembled into DXF sub-entities,
    as defined by the current point style $PDMODE.

    Decomposed entity types including sub-entities:

        - INSERT
        - DIMENSION
        - LEADER
        - MLEADER
        - MLINE

    Decomposition of XREF, UNDERLAY and ACAD_TABLE entities is not supported.

    """

    def insert(i: 'Insert') -> Iterable[DXFEntity]:
        yield from i.attribs
        yield from i.virtual_entities()

    for entity in entities:
        dxftype = entity.dxftype()
        # ignore this virtual_entities() methods:
        if dxftype in ('POINT', 'LWPOLYLINE', 'POLYLINE'):
            yield entity
        elif dxftype == 'INSERT':
            entity = cast('Insert', entity)
            if entity.mcount > 1:
                for virtual_insert in entity.multi_insert():
                    yield from insert(virtual_insert)
            else:
                yield from insert(entity)
        elif hasattr(entity, 'virtual_entities'):
            # could contain block references:
            yield from recursive_decompose(entity.virtual_entities())
        # As long as MLeader.virtual_entities() is not implemented,
        # use existing proxy graphic:
        elif dxftype in ('MLEADER', 'MULTILEADER') and entity.proxy_graphic:
            yield from ProxyGraphic(
                entity.proxy_graphic, entity.doc).virtual_entities()
        else:
            yield entity


def to_primitives(entities: Iterable[DXFEntity],
                  max_flattening_distance=None) -> Iterable[AbstractPrimitive]:
    """ Disassemble DXF entities into path/mesh primitive objects. Yields
    unsupported entities as empty primitives, see :func:`make_primitive`.
    """
    for e in entities:
        # Special handling for HATCH required, because a HATCH entity can not be
        # reduced into a single path or mesh.
        if e.dxftype() == 'HATCH':
            # noinspection PyTypeChecker
            yield from _hatch_primitives(e, max_flattening_distance)
        else:
            yield make_primitive(e, max_flattening_distance)


def to_vertices(primitives: Iterable[AbstractPrimitive]) -> Iterable[Vec3]:
    """ Disassemble path/mesh primitive objects into vertices. """
    for p in primitives:
        yield from p.vertices()


def _hatch_primitives(
        hatch: 'Hatch',
        max_flattening_distance=None) -> Iterable[AbstractPrimitive]:
    """ Yield all HATCH boundary paths as separated Path() objects. """
    ocs = hatch.ocs()
    elevation = hatch.dxf.elevation.z
    for boundary in hatch.paths:
        yield PathPrimitive(
            Path.from_hatch_boundary_path(boundary, ocs, elevation),
            hatch,
            max_flattening_distance
        )
