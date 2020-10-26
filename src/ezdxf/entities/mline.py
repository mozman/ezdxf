# Copyright (c) 2018-2020, Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional
from collections import OrderedDict, namedtuple
import math

from ezdxf.lldxf import const
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.tags import Tags, group_tags
from ezdxf.math import NULLVEC, X_AXIS, Y_AXIS, Z_AXIS, Vertex, Vector
from .dxfentity import base_class, SubclassProcessor
from .dxfobj import DXFObject
from .dxfgfx import DXFGraphic, acdb_entity
from .objectcollection import ObjectCollection
from ezdxf.entities.factory import register_entity
import logging

if TYPE_CHECKING:
    from ezdxf.eztypes import (
        TagWriter, Drawing, DXFNamespace, EntityQuery, BaseLayout, Matrix44
    )

__all__ = ['MLine', 'MLineVertex', 'MLineStyle', 'MLineStyleCollection']

# Usage example: CADKitSamples\Lock-Off.dxf

logger = logging.getLogger('ezdxf')

acdb_mline = DefSubclass('AcDbMline', OrderedDict({
    'style_name': DXFAttr(2, default='Standard'),
    'style_handle': DXFAttr(340),
    'scale_factor': DXFAttr(40, default=1),

    # Justification
    # 0 = Top (Right)
    # 1 = Zero (Center)
    # 2 = Bottom (Left)
    'justification': DXFAttr(70, default=0),

    # Flags (bit-coded values):
    # 1 = Has at least one vertex (code 72 is greater than 0)
    # 2 = Closed
    # 4 = Suppress start caps
    # 8 = Suppress end caps
    'flags': DXFAttr(71, default=1),

    # Number of MLINE vertices
    'count': DXFAttr(72, xtype=XType.callback, getter='__len__'),

    # Number of elements in MLINESTYLE definition
    'style_element_count': DXFAttr(73, default=2),

    # start location in WCS!
    'start_location': DXFAttr(10, xtype=XType.callback,
                              getter='start_location'),

    # Normal vector of the entity plane, but all vertices in WCS!
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Z_AXIS),

    # MLine data:
    # 11: vertex coordinates
    #     Multiple entries; one entry for each vertex.
    # 12: Direction vector of segment starting at this vertex
    #     Multiple entries; one for each vertex.
    # 13: Direction vector of miter at this vertex
    #     Multiple entries: one for each vertex.
    # 74: Number of parameters for this element,
    #     repeats for each element in segment
    # 41: Element parameters,
    #     repeats based on previous code 74
    # 75: Number of area fill parameters for this element,
    #     repeats for each element in segment
    # 42: Area fill parameters,
    #     repeats based on previous code 75
}))


# For information about line- and fill parametrization see comments in class
# MLineVertex().
#
# The 2 group codes in mline entities and mlinestyle objects are redundant
# fields. These groups should not be modified under any circumstances, although
# it is safe to read them and use their values. The correct fields to modify
# are as follows:
#
# Mline
# The 340 group in the same object, which indicates the proper MLINESTYLE
# object.
#
# Mlinestyle
# The 3 group value in the MLINESTYLE dictionary, which precedes the 350 group
# that has the handle or entity name of
# the current mlinestyle.

# Facts and assumptions not clearly defined by the DXF reference:
# - the reference line is defined by the group code 11 points (fact)
# - all line segments are parallel to the reference line (assumption)
# - all line vertices are located in the same plane, the orientation of the plane
#   is defined by the extrusion vector (assumption)
# - the scale factor is applied to to all geometries
# - the start- and end angle (MLineStyle) is also applied to the first and last
#   miter direction vector
# - the last two points mean: all geometries and direction vectors can be used
#   as stored in the DXF file no additional scaling or rotation is necessary
#   for the MLINE rendering. Disadvantage: minor changes of DXF attributes
#   require a refresh of the MLineVertices.

# Ezdxf does not support the creation of line-break (gap) features, but will be
# preserve this data if the MLINE stays unchanged.
# Editing the MLINE entity by ezdxf removes the line-break features (gaps).


class MLineVertex:
    def __init__(self):
        self.location: Vector = NULLVEC
        self.line_direction: Vector = X_AXIS
        self.miter_direction: Vector = Y_AXIS

        # Line parametrization (74/41)
        # ----------------------------
        # The line parameterization is a list of float values.
        # The list may contain zero or more items.
        #
        # The first value (miter-offset) is the distance from the vertex
        # location along the miter direction vector to the point where the
        # line element's path intersects the miter vector.
        #
        # The next value (line-start-offset) is the distance along the line
        # direction from the miter/line path intersection point to the actual
        # start of the line element.
        #
        # The next value (dash-length) is the distance from the start of the
        # line element (dash) to the first break (or gap) in the line element.
        # The successive values continue to list the start and stop points of
        # the line element in this segment of the mline.
        # Linetypes do not affect the line parametrization.
        #
        # [miter-offset, line-start-offset, dash-length, gap-length, dash-length, ...]
        self.line_params: List[float] = []
        """ The line parameterization is a list of float values.
        The list may contain zero or more items.
        """

        # Fill parametrization (75/42)
        # ----------------------------
        #
        # The fill parameterization is also a list of float values.
        # Similar to the line parameterization, it describes the
        # parameterization of the fill area for this mline segment.
        # The values are interpreted identically to the line parameters and when
        # taken as a whole for all line elements in the mline segment, they
        # define the boundary of the fill area for the mline segment.
        #
        # A common example of the use of the fill mechanism is when an
        # unfilled mline crosses over a filled mline and "mledit" is used to
        # cause the filled mline to appear unfilled in the crossing area.
        # This would result in two fill parameters for each line element in the
        # affected mline segment; one for the fill stop and one for the fill
        # start.
        #
        # [dash-length, gap-length, ...]?
        self.fill_params: List[float] = []

    def __copy__(self) -> 'MLineVertex':
        vtx = self.__class__()
        vtx.location = self.location
        vtx.line_direction = self.line_direction
        vtx.miter_direction = self.miter_direction
        vtx.line_params = list(self.line_params)
        vtx.fill_params = list(self.fill_params)
        return vtx

    copy = __copy__

    @classmethod
    def load(cls, tags: Tags) -> 'MLineVertex':
        vtx = MLineVertex()
        line_params = []
        line_params_count = 0
        fill_params = []
        fill_params_count = 0
        for code, value in tags:
            if code == 11:
                vtx.location = value
            elif code == 12:
                vtx.line_direction = value
            elif code == 13:
                vtx.miter_direction = value
            elif code == 74:
                line_params_count = value
                if line_params_count == 0:
                    vtx.line_params.append(tuple())
                else:
                    line_params = []
            elif code == 41:
                line_params.append(value)
                line_params_count -= 1
                if line_params_count == 0:
                    vtx.line_params.append(tuple(line_params))
                    line_params = []
            elif code == 75:
                fill_params_count = value
                if fill_params_count == 0:
                    vtx.fill_params.append(tuple())
                else:
                    fill_params = []
            elif code == 42:
                fill_params.append(value)
                fill_params_count -= 1
                if fill_params_count == 0:
                    vtx.fill_params.append(tuple(fill_params))
        return vtx

    def export_dxf(self, tagwriter: 'TagWriter'):
        tagwriter.write_vertex(11, self.location)
        tagwriter.write_vertex(12, self.line_direction)
        tagwriter.write_vertex(13, self.miter_direction)
        for line_params, fill_params in zip(self.line_params, self.fill_params):
            tagwriter.write_tag2(74, len(line_params))
            for param in line_params:
                tagwriter.write_tag2(41, param)
            tagwriter.write_tag2(75, len(fill_params))
            for param in fill_params:
                tagwriter.write_tag2(42, param)

    @classmethod
    def new(cls, start: Vertex, line_direction: Vertex, miter_direction: Vertex,
            line_params: Iterable = None,
            fill_params: Iterable = None) -> 'MLineVertex':
        vtx = MLineVertex()
        vtx.location = Vector(start)
        vtx.line_direction = Vector(line_direction)
        vtx.miter_direction = Vector(miter_direction)
        vtx.line_params = list(line_params or [])
        vtx.fill_params = list(fill_params or [])
        if len(vtx.line_params) != len(vtx.fill_params):
            raise const.DXFValueError(
                'Count mismatch of line- and fill parameters')
        return vtx


@register_entity
class MLine(DXFGraphic):
    DXFTYPE = 'MLINE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_mline)
    TOP = const.MLINE_TOP
    ZERO = const.MLINE_ZERO
    BOTTOM = const.MLINE_BOTTOM
    LEFT = const.MLINE_LEFT
    CENTER = const.MLINE_CENTER
    RIGHT = const.MLINE_RIGHT
    HAS_VERTICES = const.MLINE_HAS_VERTICES
    CLOSED = const.MLINE_CLOSED
    SUPPRESS_START_CAPS = const.MLINE_SUPPRESS_START_CAPS
    SUPPRESS_END_CAPS = const.MLINE_SUPPRESS_END_CAPS

    def __init__(self):
        super().__init__()
        self.vertices: List[MLineVertex] = []

    def __len__(self):
        """ Count of MLINE vertices. """
        return len(self.vertices)

    def _copy_data(self, entity: 'MLine') -> None:
        entity.vertices = [v.copy() for v in self.vertices]

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = processor.load_dxfattribs_into_namespace(dxf, acdb_mline)
            self.load_vertices(tags)
        return dxf

    def load_vertices(self, tags: Tags) -> None:
        self.vertices.extend(
            MLineVertex.load(tags) for tags in group_tags(tags, splitcode=11)
        )

    def preprocess_export(self, tagwriter: 'TagWriter') -> bool:
        # Do not export MLines without vertices
        return len(self.vertices) > 1
        # todo: check if line- and fill parametrization is compatible with
        #  MLINE style, requires same count of elements!

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        # ezdxf does not export MLINE entities without vertices,
        # see method preprocess_export()
        self.set_flag_state(self.HAS_VERTICES, True)
        super().export_entity(tagwriter)
        tagwriter.write_tag2(const.SUBCLASS_MARKER, acdb_mline.name)
        self.dxf.export_dxf_attribs(tagwriter, acdb_mline.attribs.keys())
        self.export_vertices(tagwriter)

    def export_vertices(self, tagwriter: 'TagWriter') -> None:
        for vertex in self._vertices:
            vertex.export_dxf(tagwriter)

    @property
    def is_closed(self) -> bool:
        """ Returns ``True`` if MLINE is closed.
        Compatibility interface to :class:`Polyline`
        """
        return self.get_flag_state(self.CLOSED)

    def close(self, state: bool = True) -> None:
        """ Get/set closed state of MLINE and update geometry accordingly.
        Compatibility interface to :class:`Polyline`
        """
        state = bool(state)
        if state != self.is_closed:
            self.set_flag_state(self.CLOSED, state)
            self.update_geometry()

    @property
    def start_caps(self) -> bool:
        """ Get/Set start caps state. ``True`` to enable start caps and
        ``False`` tu suppress start caps. """
        return not self.get_flag_state(self.SUPPRESS_START_CAPS)

    @start_caps.setter
    def start_caps(self, value: bool) -> None:
        """ Set start caps state. """
        self.set_flag_state(self.SUPPRESS_START_CAPS, not bool(value))

    @property
    def end_caps(self) -> bool:
        """ Get/Set end caps state. ``True`` to enable end caps and
        ``False`` tu suppress start caps."""
        return not self.get_flag_state(self.SUPPRESS_END_CAPS)

    @end_caps.setter
    def end_caps(self, value: bool) -> None:
        """ Set start caps state. """
        self.set_flag_state(self.SUPPRESS_END_CAPS, not bool(value))

    def set_scale_factor(self, value: float) -> None:
        """ Set the scale factor and update geometry accordingly. """
        value = float(value)
        if not math.isclose(self.dxf.scale_factor, value):
            self.dxf.scale_factor = value
            self.update_geometry()

    def set_justification(self, value: int) -> None:
        """ Set MLINE justification and update geometry accordingly.
        See :attr:`dxf.justification` for valid settings.
        """
        value = int(value)
        if self.dxf.justification != value:
            self.dxf.justification = value
            self.update_geometry()

    @property
    def style(self) -> Optional['MLineStyle']:
        """ Get associated MLINESTYLE. """
        if self.doc is None:
            return None
        _style = self.doc.entitydb.get(self.dxf.style_handle)
        if _style is None:
            _style = self.doc.mline_styles.get(self.dxf.style_name)
        return _style

    def set_style(self, name: str) -> None:
        """ Set MLINESTYLE by name and update geometry accordingly.
        The MLINESTYLE definition must exist.
        """
        if self.doc is None:
            logger.debug("Can't change style of unbounded MLINE entity.")
            return
        try:
            style = self.doc.mline_styles.get(name)
        except const.DXFKeyError:
            raise const.DXFValueError(f'Undefined MLINE style: {name}')

        # Line- and fill parametrization depends on the count of
        # elements, a change in the number of elements triggers a
        # reset of the parametrization:
        old_style = self.style
        new_element_count = len(style.elements)
        reset = False
        if old_style:
            # Do not trust the stored "style_element_count" value
            reset = len(self.style.elements) != new_element_count

        self.dxf.style_name = name
        self.dxf.style_handle = style.dxf.handle
        self.dxf.style_element_count = new_element_count
        if reset:
            locations = self.get_locations()
            self.clear()
            self.extend(locations)

    def start_location(self) -> Vector:
        """ Returns the start location of the reference line. Callback function
        for :attr:`dxf.start_location`.
        """
        if len(self.vertices):
            return self.vertices[0].location
        else:
            return NULLVEC

    def get_locations(self) -> List[Vector]:
        """ Returns the vertices of the reference line. """
        return [v.location for v in self.vertices]

    def extend(self, vertices: Iterable['Vertex']) -> None:
        """ Append multiple vertices to the reference line. """
        vertices = Vector.list(vertices)
        if not vertices:
            return
        all_vertices = []
        if len(self):
            all_vertices.extend(self.get_locations())
        all_vertices.extend(vertices)
        self.generate_geometry(all_vertices)

    def update_geometry(self) -> None:
        """ Regenerate the MLINE geometry based on current settings. """
        self.generate_geometry(self.get_locations())

    def generate_geometry(self, vertices: List[Vector]) -> None:
        """ Regenerate the MLINE geometry for new reference line defined by
        `vertices`.
        """
        # This first implementation works only in the xy-plane!
        if len(vertices) == 0:
            self.clear()
            return
        elif len(vertices) == 1:
            self.vertices = [MLineVertex.new(vertices[0], X_AXIS, Y_AXIS)]
            return

        def rotate(miter_dir: Vector, deg_angle: float) -> Vector:
            return Vector.from_deg_angle(miter_dir.angle_deg + (deg_angle - 90))

        style = self.style
        start_angle = style.dxf.start_angle
        end_angle = style.dxf.end_angle

        line_directions = [
            (v2 - v1).normalize() for v1, v2 in
            zip(vertices, vertices[1:])
        ]
        miter_directions = [
            rotate(line_directions[0].orthogonal(), start_angle)]
        for d1, d2 in zip(line_directions, line_directions[1:]):
            miter_directions.append(((d1 + d2) * 0.5).normalize())
        miter_directions.append(
            rotate(line_directions[-1].orthogonal(), end_angle))
        line_directions.append(line_directions[-1])
        self.vertices = [
            MLineVertex.new(v, d, m)
            for v, d, m in zip(vertices, line_directions, miter_directions)
        ]
        self._update_line_parametrization()

    def _update_line_parametrization(self):
        # calculate intersections of miter and line elements
        scale = self.dxf.scale_factor
        style = self.style

        justification = self.dxf.justification
        # 0 = Top
        # 1 = Zero
        # 2 = Bottom
        offsets = [e.offset for e in style.elements]
        min_offset = min(offsets)
        max_offset = max(offsets)
        if justification == 0:
            shift = abs(min_offset)
        elif justification == 1:
            shift = (max_offset - min_offset) / 2 - max_offset
        else:
            shift = -abs(max_offset)

        for vertex in self.vertices:
            normal_vector = vertex.line_direction.orthogonal()
            stretch = vertex.miter_direction.project(
                normal_vector).magnitude * scale
            vertex.line_params = [
                ((element.offset * stretch) + shift, 0.0) for element in
                style.elements
            ]

    def clear(self) -> None:
        """ Remove all MLINE vertices. """
        self.vertices.clear()

    def remove_dependencies(self, other: 'Drawing' = None) -> None:
        """ Remove all dependencies from current document.

        (internal API)
        """
        if not self.is_alive:
            return

        super().remove_dependencies(other)
        self.dxf.style_handle = '0'
        if other:
            style = other.mline_styles.get(self.dxf.style_name)
            if style:
                self.dxf.style_handle = style.dxf.handle
                return
        self.dxf.style_name = 'Standard'

    def transform(self, m: 'Matrix44') -> 'DXFGraphic':
        """ Transform MLINE entity by transformation matrix `m` inplace.
        """
        raise NotImplemented()

    def virtual_entities(self) -> Iterable[DXFGraphic]:
        """ Yields 'virtual' parts of MLINE as LINE, ARC and HATCH entities.

        This entities are located at the original positions, but are not stored
        in the entity database, have no handle and are not assigned to any
        layout.

        """
        from ezdxf.render.mline import virtual_entities
        return virtual_entities(self)

    def explode(self, target_layout: 'BaseLayout' = None) -> 'EntityQuery':
        """ Explode parts of MLINE as LINE, ARC and HATCH entities into target
        layout, if target layout is ``None``, the target layout is the layout
        of the MLINE.

        Returns an :class:`~ezdxf.query.EntityQuery` container with all DXF parts.

        Args:
            target_layout: target layout for DXF parts, ``None`` for same layout
                as source entity.
        """
        from ezdxf.explode import explode_entity
        return explode_entity(self, target_layout)


acdb_mline_style = DefSubclass('AcDbMlineStyle', {
    'name': DXFAttr(2, default='Standard'),

    # Flags (bit-coded):
    # 1 =Fill on
    # 2 = Display miters
    # 16 = Start square end (line) cap
    # 32 = Start inner arcs cap
    # 64 = Start round (outer arcs) cap
    # 256 = End square (line) cap
    # 512 = End inner arcs cap
    # 1024 = End round (outer arcs) cap
    'flags': DXFAttr(70, default=0),

    # Style description (string, 255 characters maximum):
    'description': DXFAttr(3, default=''),

    # Fill color (integer, default = 256):
    'fill_color': DXFAttr(62, default=256),

    # Start angle (real, default is 90 degrees):
    'start_angle': DXFAttr(51, default=90),

    # End angle (real, default is 90 degrees):
    'end_angle': DXFAttr(52, default=90),

    # 71: Number of elements
    # 49: Element offset (real, no default).
    #     Multiple entries can exist; one entry for each element
    # 62: Element color (integer, default = 0).
    #     Multiple entries can exist; one entry for each element
    # 6:  Element linetype (string, default = BYLAYER).
    #     Multiple entries can exist; one entry for each element
})

MLineStyleElement = namedtuple('MLineStyleElement', 'offset color linetype')


class MLineStyleElements:
    def __init__(self, tags: Tags = None):
        self.elements: List[MLineStyleElement] = []
        if tags:
            for e in self.parse_tags(tags):
                data = MLineStyleElement(e.get('offset', 1.), e.get('color', 0),
                                         e.get('linetype', 'BYLAYER'))
                self.elements.append(data)

    def __len__(self):
        return len(self.elements)

    def __getitem__(self, item):
        return self.elements[item]

    def export_dxf(self, tagwriter: 'TagWriter'):
        write_tag = tagwriter.write_tag2
        write_tag(71, len(self.elements))
        for offset, color, linetype in self.elements:
            write_tag(49, offset)
            write_tag(62, color)
            write_tag(6, linetype)

    def append(self, offset: float, color: int = 0,
               linetype: str = 'BYLAYER') -> None:
        """ Append a new line element.

        Args:
            offset: normal offset from an imaginary base line, not to be
                confused with the MLINE reference line, positive and negative
                offsets are valid.
            color: :ref:`ACI` value
            linetype: linetype name

        """
        self.elements.append(MLineStyleElement(
            float(offset), int(color), str(linetype)))

    @staticmethod
    def parse_tags(tags: Tags) -> Iterable[Dict]:
        collector = None
        for code, value in tags:
            if code == 49:
                if collector is not None:
                    yield collector
                collector = {'offset': value}
            elif code == 62:
                collector['color'] = value
            elif code == 6:
                collector['linetype'] = value
        if collector is not None:
            yield collector


@register_entity
class MLineStyle(DXFObject):
    DXFTYPE = 'MLINESTYLE'
    DXFATTRIBS = DXFAttributes(base_class, acdb_mline_style)
    FILL = const.MLINESTYLE_FILL
    MITER = const.MLINESTYLE_MITER
    START_SQUARE = const.MLINESTYLE_START_SQARE
    START_INNER_ARC = const.MLINESTYLE_START_INNER_ARC
    START_ROUND = const.MLINESTYLE_START_ROUND
    END_SQUARE = const.MLINESTYLE_END_SQUARE
    END_INNER_ARC = const.MLINESTYLE_END_INNER_ARC
    END_ROUND = const.MLINESTYLE_END_ROUND

    def __init__(self):
        super().__init__()
        self.elements = MLineStyleElements()

    def copy(self):
        raise const.DXFTypeError('Copying of MLINESTYLE not supported.')

    def load_dxf_attribs(
            self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor is None:
            return dxf

        tags = processor.load_dxfattribs_into_namespace(dxf, acdb_mline_style)
        self.elements = MLineStyleElements(tags)
        return dxf

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        super().export_entity(tagwriter)
        tagwriter.write_tag2(const.SUBCLASS_MARKER, acdb_mline_style.name)
        self.dxf.export_dxf_attribs(tagwriter, acdb_mline_style.attribs.keys())
        self.elements.export_dxf(tagwriter)


class MLineStyleCollection(ObjectCollection):
    def __init__(self, doc: 'Drawing'):
        super().__init__(doc, dict_name='ACAD_MLINESTYLE',
                         object_type='MLINESTYLE')
        self.create_required_entries()

    def create_required_entries(self) -> None:
        if 'Standard' not in self.object_dict:
            entity: MLineStyle = self.new('Standard')
            entity.elements.append(.5, 256)
            entity.elements.append(-.5, 256)
