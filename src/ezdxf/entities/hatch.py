# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-03-08
from typing import TYPE_CHECKING, List, Tuple, Union, Sequence, Iterable, Optional
from contextlib import contextmanager
import math
import copy
from ezdxf.math import Vector, Vec2, Matrix44, reflect_angle_x_deg
from ezdxf.math.transformtools import OCSTransform, NonUniformScalingError
from ezdxf.tools.rgb import rgb2int, int2rgb
from ezdxf.tools import pattern
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.tags import Tags, group_tags
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000, DXF2004, DXF2010
from ezdxf.lldxf import const
from ezdxf.math.bspline import bspline_control_frame
from ezdxf.math.bulge import bulge_to_arc
from ezdxf.math import ellipse
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes import TagWriter, DXFNamespace, Drawing, RGB, DXFEntity, Vertex

TPath = Union['PolylinePath', 'EdgePath']

__all__ = ['Hatch', 'Gradient', 'Pattern']

acdb_hatch = DefSubclass('AcDbHatch', {
    # 3D point (X and Y always equal 0, Z represents the elevation)
    'elevation': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),  # OCS

    # Extrusion direction (optional; default = 0, 0, 1)
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1)),

    # Hatch pattern name
    'pattern_name': DXFAttr(2, default='SOLID'),  # for solid fill

    # HATCH: Solid fill flag (0 = pattern fill; 1 = solid fill)
    # MPolygon: the version of MPolygon
    'solid_fill': DXFAttr(70, default=1, alias='mp_version'),

    # MPolygon: pattern fill color as the ACI
    'mp_pattern_fill_color': DXFAttr(63, default=1, optional=True),

    # HATCH: Associativity flag (0 = non-associative; 1 = associative)
    # MPolygon: solid-fill flag (0 = lacks solid fill; 1 = has solid fill)
    'associative': DXFAttr(71, default=0, alias='mp_solid_fill'),

    # 91: Number of boundary paths (loops)
    # following: Boundary path data. Repeats number of times specified by code 91. See Boundary Path Data

    # Hatch style:
    # 0 = Hatch “odd parity” area (Normal style)
    # 1 = Hatch outermost area only (Outer style)
    # 2 = Hatch through entire area (Ignore style)
    'hatch_style': DXFAttr(75, default=const.HATCH_STYLE_NESTED),

    # Hatch pattern type:
    # 0 = User-defined
    # 1 = Predefined
    # 2 = Custom
    'pattern_type': DXFAttr(76, default=const.HATCH_TYPE_PREDEFINED),

    # Hatch pattern angle (pattern fill only) in degrees
    'pattern_angle': DXFAttr(52, default=0),

    # Hatch pattern scale or spacing (pattern fill only)
    'pattern_scale': DXFAttr(41, default=1),

    # For MPolygon, boundary annotation flag:
    # 0 = boundary is not an annotated boundary
    # 1 = boundary is an annotated boundary
    'mp_annotated_boundary': DXFAttr(73, default=0, optional=True),

    # Hatch pattern double flag (pattern fill only):
    # 0 = not double
    # 1 = double
    'pattern_double': DXFAttr(77, default=0),  # 0=not double; 1= double

    # 78: Number of pattern definition lines
    # following: Pattern line data. Repeats number of times specified by code 78. See Pattern Data

    # Pixel size used to determine the density to perform various intersection and ray casting operations in hatch
    # pattern computation for associative hatches and hatches created with the Flood method of hatching
    # removed tag (code=47, 0.0442352806926743) from Template: pixel size - caused problems in AutoCAD
    'pixel_size': DXFAttr(47, optional=True),

    # Number of seed points
    'n_seed_points': DXFAttr(98, default=0),  # number of seed points
    # 10, 20: Seed point (in OCS) 2D point (multiple entries)

    # For MPolygon, offset vector
    'mp_offset_vector': DXFAttr(11, xtype=XType.point3d, optional=True),  # OCS

    # For MPolygon, number of degenerate boundary paths (loops), where a degenerate boundary path is a border that is
    # ignored by the hatch
    'mp_degenerated_loops': DXFAttr(99, optional=True),

    # 450 Indicates solid hatch or gradient; if solid hatch, the values for the remaining codes are ignored but must be
    #     present. Optional;
    #
    # if code 450 is in the file, then the following codes must be in the file: 451, 452, 453, 460, 461, 462, and 470.
    # If code 450 is not in the file, then the following codes must not be in the file: 451, 452, 453, 460, 461, 462, and 470
    #
    #   0 = Solid hatch
    #   1 = Gradient
    #
    # 451 Zero is reserved for future use
    # 452 Records how colors were defined and is used only by dialog code:
    #
    #   0 = Two-color gradient
    #   1 = Single-color gradient
    #
    # 453 Number of colors:
    #
    #   0 = Solid hatch
    #   2 = Gradient
    #
    # 460 Rotation angle in radians for gradients (default = 0, 0)
    # 461 Gradient definition; corresponds to the Centered option on the Gradient Tab of the Boundary Hatch and Fill
    #     dialog box. Each gradient has two definitions, shifted and non-shifted. A Shift value describes the blend of
    #     the two definitions that should be used. A value of 0.0 means only the non-shifted version should be used, and
    #     a value of 1.0 means that only the shifted version should be used.
    #
    # 462 Color tint value used by dialog code (default = 0, 0; range is 0.0 to 1.0). The color tint value is a gradient
    #     color and controls the degree of tint in the dialog when the Hatch group code 452 is set to 1.
    #
    # 463 Reserved for future use:
    #
    #   0 = First value
    #   1 = Second value
    #
    # 470 String (default = LINEAR)
})

GRADIENT_CODES = {450, 451, 452, 453, 460, 461, 462, 463, 470, 421, 63}
PATH_CODES = {10, 11, 12, 13, 40, 42, 50, 51, 42, 72, 73, 74, 92, 93, 94, 95, 96, 97, 330}
PATTERN_DEFINITION_LINE_CODES = {53, 43, 44, 45, 46, 79, 49}


@register_entity
class Hatch(DXFGraphic):
    """ DXF HATCH entity """
    DXFTYPE = 'HATCH'
    DXFATTRIBS = DXFAttributes(base_class, acdb_entity, acdb_hatch)
    DEFAULT_ATTRIBS = {'color': 1, 'layer': '0'}
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self.paths = BoundaryPaths()
        self.pattern: Optional[Pattern] = None
        self.gradient: Optional[Gradient] = None
        self.seeds = []

    def _copy_data(self, entity: 'Hatch') -> None:
        """ Copy paths, pattern, gradient, seeds. """
        entity.paths = copy.deepcopy(self.paths)
        entity.pattern = copy.deepcopy(self.pattern)
        entity.gradient = copy.deepcopy(self.gradient)
        entity.seeds = copy.deepcopy(self.seeds)

    def remove_association(self):
        """ Remove associated path elements.

        .. versionadded:: 0.13

        """
        if self.dxf.associative:
            self.dxf.associative = 0
            for path in self.paths:
                path.source_boundary_objects = []

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = Tags(processor.subclasses[2][1:])  # copy without subclass marker
            tags = self.load_paths(tags)  # removes boundary path data from tags
            tags = self.load_gradient(tags)  # removes gradient data
            tags = self.load_pattern(tags)  # removes pattern tags
            tags = self.load_seeds(tags)  # removes seed tags

            # load HATCH DXF attributes from remaining tags
            tags = processor.load_tags_into_namespace(dxf, tags, acdb_hatch)
            if len(tags):
                processor.log_unprocessed_tags(tags, subclass=acdb_hatch.name)
        return dxf

    def load_paths(self, tags: Tags) -> Tags:
        # find first group code 91 = count of loops, Spline data also contains group code 91!
        try:
            start_index = tags.tag_index(91)
        except const.DXFValueError:
            raise const.DXFStructureError(
                "HATCH: Missing required DXF tag 'Number of boundary paths (loops)' (code=91).")

        path_tags = tags.collect_consecutive_tags(PATH_CODES, start=start_index + 1)
        if len(path_tags):
            self.paths = BoundaryPaths.load_tags(path_tags)
        end_index = start_index + len(path_tags) + 1
        del tags[start_index: end_index]
        return tags

    def load_pattern(self, tags: Tags) -> Tags:
        try:
            index = tags.tag_index(78)  # code 78=Number of patter definition lines
        except const.DXFValueError:  # no pattern definition lines found
            return tags

        pattern_tags = tags.collect_consecutive_tags(PATTERN_DEFINITION_LINE_CODES, start=index + 1)
        self.pattern = Pattern.load_tags(pattern_tags)

        # delete pattern data including length tag 78
        del tags[index: index + len(pattern_tags) + 1]
        return tags

    def load_gradient(self, tags: Tags) -> Tags:
        try:
            index = tags.tag_index(450)
        except const.DXFValueError:
            # no gradient data present
            return tags

        # gradient data is always at the end of the AcDbHatch subclass
        self.gradient = Gradient.load_tags(tags[index:])
        # remove gradient data
        del tags[index:]
        return tags

    def load_seeds(self, tags: Tags) -> Tags:
        try:
            start_index = tags.tag_index(98)
        except const.DXFValueError:
            return tags
        seed_data = tags.collect_consecutive_tags({98, 10, 20}, start=start_index)

        # remove seed data from tags
        del tags[start_index: start_index + len(seed_data) + 1]

        # just process vertices with group code 10
        self.seeds = [value for code, value in seed_data if code == 10]

        return tags

    def export_entity(self, tagwriter: 'TagWriter') -> None:
        """ Export entity specific data as DXF tags. """
        # base class export is done by parent class
        super().export_entity(tagwriter)
        # AcDbEntity export is done by parent class
        tagwriter.write_tag2(SUBCLASS_MARKER, acdb_hatch.name)
        self.dxf.export_dxf_attribs(tagwriter, [
            'elevation', 'extrusion', 'pattern_name', 'solid_fill', 'mp_pattern_fill_color', 'associative',
        ])
        self.paths.export_dxf(tagwriter)
        self.dxf.export_dxf_attribs(tagwriter, ['hatch_style', 'pattern_type'])
        if self.pattern:
            self.dxf.export_dxf_attribs(tagwriter, ['pattern_angle', 'pattern_scale', 'pattern_double'])
            self.pattern.export_dxf(tagwriter)
        self.dxf.export_dxf_attribs(tagwriter, ['mp_annotated_boundary', 'pixel_size'])
        self.export_seeds(tagwriter)
        self.dxf.export_dxf_attribs(tagwriter, ['mp_offset_vector', 'mp_degenerated_loops'])
        if self.gradient:
            self.gradient.export_dxf(tagwriter)

    def export_seeds(self, tagwriter: 'TagWriter'):
        tagwriter.write_tag2(98, len(self.seeds))
        for seed in self.seeds:
            tagwriter.write_vertex(10, seed[:2])

    @property
    def has_solid_fill(self) -> bool:
        """ ``True`` if hatch has a solid fill. (read only) """
        return bool(self.dxf.solid_fill)

    @property
    def has_pattern_fill(self) -> bool:
        """ ``True`` if hatch has a pattern fill. (read only) """
        return not bool(self.dxf.solid_fill)

    @property
    def has_gradient_data(self) -> bool:
        """ ``True`` if hatch has a gradient fill. A hatch with gradient fill has also a solid fill. (read only) """
        return bool(self.gradient)

    @property
    def bgcolor(self) -> Optional['RGB']:
        """
        Property background color as ``(r, g, b)`` tuple, rgb values in range 0..255 (read/write/del)

        usage::

            color = hatch.bgcolor  # get background color as (r, g, b) tuple
            hatch.bgcolor = (10, 20, 30)  # set background color
            del hatch.bgcolor  # delete background color


        """
        try:
            xdata_bgcolor = self.get_xdata('HATCHBACKGROUNDCOLOR')
        except const.DXFValueError:
            return None
        color = xdata_bgcolor.get_first_value(1071, 0)
        return int2rgb(color)

    @bgcolor.setter
    def bgcolor(self, rgb: 'RGB') -> None:
        color_value = rgb2int(rgb) | -0b111110000000000000000000000000  # it's magic

        self.discard_xdata('HATCHBACKGROUNDCOLOR')
        self.set_xdata('HATCHBACKGROUNDCOLOR', [(1071, color_value)])

    @bgcolor.deleter
    def bgcolor(self) -> None:
        self.discard_xdata('HATCHBACKGROUNDCOLOR')

    # just for compatibility
    @contextmanager
    def edit_boundary(self) -> 'BoundaryPaths':
        """ Context manager to edit hatch boundary data, yields a :class:`BoundaryPaths` object. """
        yield self.paths

    def set_solid_fill(self, color: int = 7, style: int = 1, rgb: 'RGB' = None):
        """
        Set :class:`Hatch` to solid fill mode and removes all gradient and pattern fill related data.

        Args:
            color: :ref:`ACI`, (``0`` = BYBLOCK; ``256`` = BYLAYER)
            style: hatch style (``0`` = normal; ``1`` = outer; ``2`` = ignore)
            rgb: true color value as ``(r, g, b)`` tuple - has higher priority than `color``.
                 True color support requires DXF R2000.

        """
        self.gradient = None
        if self.has_pattern_fill:
            self.pattern = None
            self.dxf.solid_fill = 1

        self.dxf.color = color  # if a rgb value is present, the color value is ignored by AutoCAD
        self.dxf.hatch_style = style
        self.dxf.pattern_name = 'SOLID'
        self.dxf.pattern_type = const.HATCH_TYPE_PREDEFINED
        if rgb is not None:  # if a rgb value is present, the color value is ignored by AutoCAD
            self.rgb = rgb  # rgb should be a (r, g, b) tuple

    def get_gradient(self):
        """ Returns gradient data as :class:`GradientData` object. """
        return self.gradient

    def set_gradient(self,
                     color1: 'RGB' = (0, 0, 0),
                     color2: 'RGB' = (255, 255, 255),
                     rotation: float = 0.,
                     centered: float = 0.,
                     one_color: int = 0,
                     tint: float = 0.,
                     name: str = 'LINEAR') -> None:
        """
        Set :class:`Hatch` to gradient fill mode and removes all pattern fill related data. Gradient support requires
        DXF DXF R2004. A gradient filled hatch is also a solid filled hatch.

        Valid gradient type names are:


            - ``'LINEAR'``
            - ``'CYLINDER'``
            - ``'INVCYLINDER'``
            - ``'SPHERICAL'``
            - ``'INVSPHERICAL'``
            - ``'HEMISPHERICAL'``
            - ``'INVHEMISPHERICAL'``
            - ``'CURVED'``
            - ``'INVCURVED'``

        Args:
            color1: ``(r, g, b)`` tuple for first color, rgb values as int in range 0..255
            color2: ``(r, g, b)`` tuple for second color, rgb values as int in range 0..255
            rotation: rotation in degrees
            centered: determines whether the gradient is centered or not
            one_color: ``1`` for gradient from `color1` to tinted `color1``
            tint: determines the tinted target `color1` for a one color gradient. (valid range ``0.0`` to ``1.0``)
            name: name of gradient type, default ``'LINEAR'``

        """
        if self.doc is not None and self.drawing.dxfversion < DXF2004:
            raise const.DXFVersionError("Gradient support requires DXF R2004")
        if name not in const.GRADIENT_TYPES:
            raise const.DXFValueError('Invalid gradient type name: %s' % name)

        self.pattern = None
        self.dxf.solid_fill = 1
        self.dxf.pattern_name = 'SOLID'
        self.dxf.pattern_type = const.HATCH_TYPE_PREDEFINED

        gradient = Gradient()
        gradient.color1 = color1
        gradient.color2 = color2
        gradient.one_color = one_color
        gradient.rotation = rotation
        gradient.centered = centered
        gradient.tint = tint
        gradient.name = name
        self.gradient = gradient

    # just for compatibility
    @contextmanager
    def edit_gradient(self) -> 'Gradient':
        """ Context manager to edit hatch gradient data, yields a :class:`GradientData` object. """
        if not self.gradient:
            raise const.DXFValueError('HATCH has no gradient data.')
        yield self.gradient

    def set_pattern_fill(self, name: str, color: int = 7, angle: float = 0., scale: float = 1., double: int = 0,
                         style: int = 1, pattern_type: int = 1, definition=None) -> None:
        """
        Set :class:`Hatch` to pattern fill mode. Removes all gradient related data. The pattern definition
        should be designed for scaling factor 1.

        Args:
            name: pattern name as string
            color: pattern color as :ref:`ACI`
            angle: angle of pattern fill in degrees
            scale: pattern scaling as float
            double: double size flag
            style: hatch style (``0`` = normal; ``1`` = outer; ``2`` = ignore)
            pattern_type: pattern type (``0`` = user-defined; ``1`` = predefined; ``2`` = custom) ???
            definition: list of definition lines and a definition line is a 4-tuple [angle, base_point,
                        offset, dash_length_items], see :meth:`set_pattern_definition`

        """
        self.gradient = None
        self.dxf.solid_fill = 0
        self.dxf.pattern_name = name
        self.dxf.color = color
        self.dxf.pattern_scale = float(scale)
        self.dxf.pattern_angle = float(angle)
        self.dxf.pattern_double = int(double)
        self.dxf.hatch_style = style
        self.dxf.pattern_type = pattern_type

        if definition is None:
            # get pattern definition from acad standard pattern, default is 'ANSI31'
            predefiend_pattern = pattern.load()
            definition = predefiend_pattern.get(name, predefiend_pattern['ANSI31'])
        self.set_pattern_definition(definition, factor=self.dxf.pattern_scale)

    # just for compatibility
    @contextmanager
    def edit_pattern(self) -> 'Pattern':
        """ Context manager to edit hatch pattern data, yields a :class:`PatternData` object. """
        if not self.pattern:
            raise const.DXFValueError('Solid fill HATCH has no pattern data.')
        yield self.pattern

    def set_pattern_definition(self, lines: Sequence, factor: float = 1) -> None:
        """
        Setup hatch patten definition by a list of definition lines and  a definition line is a 4-tuple [angle,
        base_point, offset, dash_length_items], the pattern definition should be designed for scaling factor 1.

            - angle: line angle in degrees
            - base-point: 2-tuple (x, y)
            - offset: 2-tuple (dx, dy)
            - dash_length_items: list of dash items (item > 0 is a line, item < 0 is a gap and item == 0.0 is a point)

        Args:
            lines: list of definition lines
            factor: pattern scaling factor

        """
        if factor != 1:
            lines = pattern.scale_pattern(lines, factor)
        self.pattern = Pattern([PatternLine(line[0], line[1], line[2], line[3]) for line in lines])

    # just for compatibility
    def get_seed_points(self) -> List:
        """
        Returns seed points as list of ``(x, y)`` points, I don't know why there can be more than one seed point.
        All points in :ref:`OCS` (:attr:`Hatch.dxf.elevation` is the Z value).
        """
        return self.seeds

    def set_seed_points(self, points: Sequence[Tuple[float, float]]) -> None:
        """
        Set seed points, `points` is a list of ``(x, y)`` tuples, I don't know why there can be more than one
        seed point. All points in :ref:`OCS` (:attr:`Hatch.dxf.elevation` is the Z value)
        """
        if len(points) < 1:
            raise const.DXFValueError(
                "Param points should be a collection of 2D points and requires at least one point.")
        self.seeds = list(points)
        self.dxf.n_seed_points = len(self.seeds)

    def transform(self, m: 'Matrix44') -> 'Hatch':
        """
        Transform HATCH entity by transformation matrix `m` inplace.

        Non uniform scaling for hatches containing arc- or ellipse edges is not correct,
        but at least do not produce invalid DXF files.

        .. versionadded:: 0.13

        """
        dxf = self.dxf
        ocs = OCSTransform(dxf.extrusion, m)

        elevation = Vector(dxf.elevation).z
        self.paths.transform(ocs, elevation=elevation)
        dxf.elevation = ocs.transform_vertex(Vector(0, 0, elevation)).replace(x=0, y=0)
        dxf.extrusion = ocs.new_extrusion
        # todo scale pattern
        return self

    def associate(self, path: TPath, entities: Iterable['DXFEntity']):
        """ Set association from hatch boundary `path` to DXF geometry `entities`.

        A HATCH entity can be associative to a base geometry, this association is **not** maintained nor
        verified by `ezdxf`, so if you modify the base geometry the geometry of the boundary
        path is not updated and no verification is done to check if the associated geometry matches
        the boundary path, this opens many possibilities to create invalid DXF files: USE WITH CARE!

        .. versionadded:: 0.11

        """
        self.dxf.associative = 1
        hatch_dxf_handle = self.dxf.handle
        for entity in entities:
            path.source_boundary_objects.append(entity.dxf.handle)
            entity.append_reactor_handle(hatch_dxf_handle)


class BoundaryPaths:
    def __init__(self, paths: List[TPath] = None):
        self.paths = paths or []  # type: List[TPath]

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, item):
        return self.paths[item]

    @classmethod
    def load_tags(cls, tags: Tags) -> 'BoundaryPaths':
        paths = []
        assert tags[0].code == 92
        grouped_path_tags = group_tags(tags, splitcode=92)
        for path_tags in grouped_path_tags:
            path_type_flags = path_tags[0].value
            is_polyline_path = bool(path_type_flags & 2)
            path = PolylinePath.load_tags(path_tags) if is_polyline_path else EdgePath.load_tags(path_tags)
            path.path_type_flags = path_type_flags
            paths.append(path)
        return cls(paths)

    def clear(self) -> None:
        """ Remove all boundary paths. """
        self.paths = []

    def add_polyline_path(self, path_vertices: Sequence[Tuple[float, float]], is_closed: bool = True,
                          flags: int = 1) -> 'PolylinePath':
        """
        Create and add a new :class:`PolylinePath` object.

        Args:
            path_vertices: list of polyline vertices as ``(x, y)`` or ``(x, y, bulge)`` tuples.
            is_closed: ``1`` for a closed polyline else ``0``
            flags: external(``1``) or outermost(``16``) or default (``0``)

        """
        new_path = PolylinePath()
        new_path.set_vertices(path_vertices, is_closed)
        new_path.path_type_flags = flags | const.BOUNDARY_PATH_POLYLINE
        self.paths.append(new_path)
        return new_path

    def add_edge_path(self, flags: int = 1) -> 'EdgePath':
        """
        Create and add a new :class:`EdgePath` object.

        Args:
            flags: external(``1``) or outermost(``16``) or default (``0``)

        """
        new_path = EdgePath()
        new_path.path_type_flags = flags
        self.paths.append(new_path)
        return new_path

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(91, len(self.paths))
        for path in self.paths:
            path.export_dxf(tagwriter)

    def transform(self, ocs: OCSTransform, elevation: float = 0) -> None:
        """ Transform HATCH boundary paths.

        These paths are 2d elements, placed in to OCS of the HATCH.

        """
        if not ocs.scale_uniform:
            self.arc_edges_to_ellipse_edges()

        for path in self.paths:
            path.transform(ocs, elevation=elevation)

    def arc_edges_to_ellipse_edges(self):
        """
        Convert polyline paths with bulge values to edge paths with line and arc edges if necessary and then
        convert arc edges to ellipse edges.

        (internal API)
        """

        def _edges(points) -> Iterable[Union[LineEdge, ArcEdge]]:
            prev_point = None
            prev_bulge = None
            for x, y, bulge in points:
                point = Vector(x, y)
                if prev_point is None:
                    prev_point = point
                    prev_bulge = bulge
                    continue

                if prev_bulge != 0:
                    arc = ArcEdge()
                    arc.center, start_angle, end_angle, arc.radius = bulge_to_arc(prev_point, point, prev_bulge)
                    chk_point = arc.center + Vec2.from_angle(start_angle, arc.radius)
                    if chk_point.isclose(prev_point, abs_tol=1e-9):
                        arc.is_counter_clockwise = 1
                    else:
                        start_angle += math.pi
                        end_angle += math.pi
                        arc.is_counter_clockwise = 0
                    arc.start_angle = math.degrees(start_angle) % 360.0
                    arc.end_angle = math.degrees(end_angle) % 360.0
                    yield arc
                else:
                    line = LineEdge()
                    line.start = (prev_point.x, prev_point.y)
                    line.end = (point.x, point.y)
                    yield line

                prev_point = point
                prev_bulge = bulge

        def to_edge_path(polyline_path) -> EdgePath:
            edge_path = EdgePath()
            vertices = list(polyline_path.vertices)
            if polyline_path.is_closed:
                vertices.append(vertices[0])
            edge_path.edges = list(_edges(vertices))
            return edge_path

        def to_ellipse(arc: ArcEdge) -> EllipseEdge:
            ellipse = EllipseEdge()
            ellipse.center = arc.center
            ellipse.ratio = 1.0
            ellipse.major_axis = (arc.radius, 0.0)
            ellipse.start_angle = arc.start_angle
            ellipse.end_angle = arc.end_angle
            ellipse.is_counter_clockwise = arc.is_counter_clockwise
            return ellipse

        for path_index, path in enumerate(self.paths):
            if path.PATH_TYPE == 'PolylinePath' and path.has_bulge():
                path = to_edge_path(path)
                self.paths[path_index] = path
            if path.PATH_TYPE == 'EdgePath':
                edges = path.edges
                for edge_index, edge in enumerate(edges):
                    if edge.EDGE_TYPE == 'ArcEdge':
                        edges[edge_index] = to_ellipse(edge)

    def has_critical_elements(self) -> bool:
        """ Returns ``True`` if any boundary path has bulge values or arc edges or ellipse edges.

        (internal API)

        """
        for path in self.paths:
            if path.PATH_TYPE == 'PolylinePath':
                return path.has_bulge()
            else:
                for edge in path.edges:
                    if edge.EDGE_TYPE in {'ArcEdge', 'EllipseEdge'}:
                        return True
        return False


def pop_source_boundary_objects_tags(path_tags: Tags) -> List[str]:
    source_boundary_object_tags = []
    while len(path_tags):
        if path_tags[-1].code in (97, 330):
            last_tag = path_tags.pop()
            if last_tag.code == 330:
                source_boundary_object_tags.append(last_tag.value)
            else:  # code == 97
                # result list does not contain the length tag!
                source_boundary_object_tags.reverse()
                return source_boundary_object_tags
        else:
            return []  # no source boundary objects found - entity is not valid for AutoCAD


def export_source_boundary_objects(tagwriter: 'TagWriter', handles: Sequence[str]):
    tagwriter.write_tag2(97, len(handles))
    for handle in handles:
        tagwriter.write_tag2(330, handle)


class PolylinePath:
    PATH_TYPE = 'PolylinePath'

    def __init__(self):
        self.path_type_flags: int = const.BOUNDARY_PATH_POLYLINE
        self.is_closed = False
        # list of 2D coordinates with bulge values (x, y, bulge); bulge default = 0.0
        self.vertices: List[Tuple[float, float, float]] = []
        self.source_boundary_objects: List[str] = []  # (330, handle) tags

    @classmethod
    def load_tags(cls, tags: Tags) -> 'PolylinePath':
        path = PolylinePath()
        path.source_boundary_objects = pop_source_boundary_objects_tags(tags)
        for tag in tags:
            code, value = tag
            if code == 10:  # vertex coordinates
                path.vertices.append((value[0], value[1], 0.0))  # (x, y, bulge); bulge default = 0.0
            elif code == 42:  # bulge value
                x, y, bulge = path.vertices.pop()  # last value
                path.vertices.append((x, y, value))  # last coordinates with new bulge value
            elif code == 72:
                pass  # ignore this value
            elif code == 73:
                path.is_closed = value
            elif code == 92:
                path.path_type_flags = value
            elif code == 93:  # number of polyline vertices
                pass  # ignore this value
        return path

    def set_vertices(self, vertices: Sequence[Sequence[float]], is_closed: bool = True) -> None:
        """ Set new `vertices` as new polyline path, a vertex has to be a ``(x, y)`` or a ``(x, y, bulge)`` tuple.
        """
        new_vertices = []
        for vertex in vertices:
            if len(vertex) == 2:
                x, y = vertex
                bulge = 0
            elif len(vertex) == 3:
                x, y, bulge = vertex
            else:
                raise const.DXFValueError("Invalid vertex format, expected (x, y) or (x, y, bulge)")
            new_vertices.append((x, y, bulge))
        self.vertices = new_vertices
        self.is_closed = is_closed

    def clear(self) -> None:
        """ Removes all vertices and all handles to associated DXF objects (:attr:`source_boundary_objects`). """
        self.vertices = []
        self.is_closed = False
        self.source_boundary_objects = []

    def has_bulge(self) -> bool:
        for x, y, bulge in self.vertices:
            if bulge != 0:
                return True
        return False

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        has_bulge = self.has_bulge()
        write_tag = tagwriter.write_tag2

        write_tag(92, int(self.path_type_flags))
        write_tag(72, int(has_bulge))
        write_tag(73, int(self.is_closed))
        write_tag(93, len(self.vertices))
        for x, y, bulge in self.vertices:
            tagwriter.write_vertex(10, (float(x), float(y)))
            if has_bulge:
                write_tag(42, float(bulge))

        export_source_boundary_objects(tagwriter, self.source_boundary_objects)

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        """ Transform polyline path.
        """
        has_non_uniform_scaling = not ocs.scale_uniform

        def _transform():
            for x, y, bulge in self.vertices:
                # PolylinePaths() with arcs should be converted to EdgePath (in BoundaryPath.transform()).
                if bulge and has_non_uniform_scaling:
                    raise NonUniformScalingError('Polyline path with arcs does not support non uniform scaling')
                v = ocs.transform_vertex(Vector(x, y, elevation))
                yield v.x, v.y, bulge

        if self.vertices:
            self.vertices = list(_transform())


class EdgePath:
    PATH_TYPE = 'EdgePath'

    def __init__(self):
        self.path_type_flags = const.BOUNDARY_PATH_DEFAULT
        self.edges = []
        self.source_boundary_objects = []

    @classmethod
    def load_tags(cls, tags: Tags) -> 'EdgePath':
        edge_path = cls()
        edge_path.source_boundary_objects = pop_source_boundary_objects_tags(tags)
        edge_groups = group_tags(tags, splitcode=72)
        for edge_tags in edge_groups:
            edge_path.edges.append(edge_path.load_edge(edge_tags))
        return edge_path

    @staticmethod
    def load_edge(tags: Tags) -> 'EdgeTypes':
        edge_type = tags[0].value
        if 0 < edge_type < 5:
            return EDGE_CLASSES[edge_type].load_tags(tags[1:])
        else:
            raise const.DXFStructureError("HATCH: unknown edge type: {}".format(edge_type))

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        """ Transform edge boundary paths.
        """
        for edge in self.edges:
            edge.transform(ocs, elevation=elevation)

    def add_line(self, start: Sequence[float], end: Sequence[float]) -> 'LineEdge':
        """
        Add a :class:`LineEdge` from `start` to `end`.

        Args:
            start: start point of line, ``(x, y)`` tuple
            end: end point of line, ``(x, y)`` tuple

        """
        line = LineEdge()
        line.start = start
        line.end = end
        self.edges.append(line)
        return line

    def add_arc(self, center: Tuple[float, float],
                radius: float = 1.,
                start_angle: float = 0.,
                end_angle: float = 360.,
                is_counter_clockwise: int = 0) -> 'ArcEdge':
        """
        Add an :class:`ArcEdge`.

        :param tuple center:
        :param float radius: radius of circle
        :param float start_angle: start angle of arc in degrees
        :param float end_angle: end angle of arc in degrees
        :param int is_counter_clockwise: 1 for yes 0 for no

        Args:
            center: center point of arc, ``(x, y)`` tuple
            radius: radius of circle
            start_angle: start angle of arc in degrees
            end_angle: end angle of arc in degrees
            is_counter_clockwise: ``1`` for counter clockwise ``0`` for clockwise orientation

        """
        arc = ArcEdge()
        arc.center = center
        arc.radius = radius
        arc.start_angle = start_angle
        arc.end_angle = end_angle
        arc.is_counter_clockwise = 1 if bool(is_counter_clockwise) else 0
        self.edges.append(arc)
        return arc

    def add_ellipse(self, center: Tuple[float, float],
                    major_axis: Tuple[float, float] = (1., 0.),
                    ratio: float = 1.,
                    start_angle: float = 0.,
                    end_angle: float = 360.,
                    is_counter_clockwise: int = 0) -> 'EllipseEdge':
        """
        Add an :class:`EllipseEdge`.

        Args:
            center: center point of ellipse, ``(x, y)`` tuple
            major_axis: vector of major axis as ``(x, y)`` tuple
            ratio: ratio of minor axis to major axis as float
            start_angle: start angle of arc in degrees
            end_angle: end angle of arc in degrees
            is_counter_clockwise: ``1`` for counter clockwise ``0`` for clockwise orientation

        """
        if ratio > 1.:
            raise const.DXFValueError("Parameter 'ratio' has to be <= 1.0")
        ellipse = EllipseEdge()
        ellipse.center = center
        ellipse.major_axis = major_axis
        ellipse.ratio = ratio
        ellipse.start_angle = start_angle
        ellipse.end_angle = end_angle
        ellipse.is_counter_clockwise = is_counter_clockwise
        self.edges.append(ellipse)
        return ellipse

    def add_spline(self, fit_points: Iterable[Tuple[float, float]] = None,
                   control_points: Iterable[Tuple[float, float]] = None,
                   knot_values: Iterable[float] = None,
                   weights: Iterable[float] = None,
                   degree: int = 3,
                   rational: int = 0,
                   periodic: int = 0,
                   start_tangent: 'Vertex' = None,
                   end_tangent: 'Vertex' = None,
                   ) -> 'SplineEdge':
        """
        Add a :class:`SplineEdge`.

        Args:
            fit_points: points through which the spline must go, at least 3 fit points are required.
                        list of ``(x, y)`` tuples
            control_points: affects the shape of the spline, mandatory amd AutoCAD crashes on invalid data.
                            list of ``(x, y)`` tuples
            knot_values: (knot vector) mandatory and AutoCAD crashes on invalid data. list of floats;
                         `ezdxf` provides two tool functions to calculate valid knot values:
                         :func:`ezdxf.math.bspline.knot_values` and
                         :func:`ezdxf.math.bspline.knot_values_uniform`
            weights: weight of control point, not mandatory, list of floats.
            degree: degree of spline (int)
            rational: ``1`` for rational spline, ``0`` for none rational spline
            periodic: ``1`` for periodic spline, ``0`` for none periodic spline
            start_tangent: start_tangent as 2d vector, optional
            end_tangent: end_tangent as 2d vector, optional

        .. warning::

            Unlike for the spline entity AutoCAD does not calculate the necessary `knot_values` for the spline edge
            itself. On the contrary, if the `knot_values` in the spline edge are missing or invalid
            AutoCAD **crashes**.

        """
        spline = SplineEdge()
        if fit_points is not None:
            spline.fit_points = list(fit_points)
        if control_points is not None:
            spline.control_points = list(control_points)
        if knot_values is not None:
            spline.knot_values = list(knot_values)
        if weights is not None:
            spline.weights = list(weights)
        spline.degree = degree
        spline.rational = int(rational)
        spline.periodic = int(periodic)
        if start_tangent is not None:
            spline.start_tangent = Vec2(start_tangent)
        if end_tangent is not None:
            spline.end_tangent = Vec2(end_tangent)
        self.edges.append(spline)
        return spline

    def add_spline_control_frame(self, fit_points: Iterable[Tuple[float, float]],
                                 degree: int = 3,
                                 method: str = 'distance',
                                 power: float = .5) -> 'SplineEdge':
        bspline = bspline_control_frame(fit_points=fit_points, degree=degree, method=method, power=power)
        return self.add_spline(
            fit_points=fit_points,
            control_points=bspline.control_points,
            knot_values=bspline.knot_values(),
        )

    def clear(self) -> None:
        """ Delete all edges."""
        self.edges = []

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(92, int(self.path_type_flags))
        tagwriter.write_tag2(93, len(self.edges))
        for edge in self.edges:
            edge.export_dxf(tagwriter)
        export_source_boundary_objects(tagwriter, self.source_boundary_objects)


def _transform_2d_ocs_vertices(ucs, vertices, elevation, extrusion) -> List[Tuple[float, float]]:
    ocs_vertices = (Vector(x, y, elevation) for x, y in vertices)
    return [(v.x, v.y) for v in ucs.ocs_points_to_ocs(ocs_vertices, extrusion=extrusion)]


class LineEdge:
    EDGE_TYPE = "LineEdge"

    def __init__(self):
        self.start = Vec2((0, 0))
        self.end = Vec2((0, 0))

    @classmethod
    def load_tags(cls, tags: Tags) -> 'LineEdge':
        edge = cls()
        for tag in tags:
            code, value = tag
            if code == 10:
                edge.start = Vec2(value)
            elif code == 11:
                edge.end = Vec2(value)
        return edge

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(72, 1)  # edge type

        x, y, *_ = self.start
        tagwriter.write_tag2(10, float(x))
        tagwriter.write_tag2(20, float(y))

        x, y, *_ = self.end
        tagwriter.write_tag2(11, float(x))
        tagwriter.write_tag2(21, float(y))

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        self.start = ocs.transform_2d_vertex(self.start, elevation)
        self.end = ocs.transform_2d_vertex(self.end, elevation)


class ArcEdge:
    EDGE_TYPE = "ArcEdge"

    def __init__(self):
        self.center = Vec2((0., 0.))
        self.radius: float = 1.
        self.start_angle: float = 0.
        self.end_angle: float = 360.
        self.is_counter_clockwise: int = 0

    @classmethod
    def load_tags(cls, tags: Tags) -> 'ArcEdge':
        edge = cls()
        for tag in tags:
            code, value = tag
            if code == 10:
                edge.center = Vec2(value)
            elif code == 40:
                edge.radius = value
            elif code == 50:
                edge.start_angle = value
            elif code == 51:
                edge.end_angle = value
            elif code == 73:
                edge.is_counter_clockwise = value
        return edge

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(72, 2)  # edge type
        x, y, *_ = self.center
        tagwriter.write_tag2(10, float(x))
        tagwriter.write_tag2(20, float(y))
        tagwriter.write_tag2(40, self.radius)
        tagwriter.write_tag2(50, self.start_angle)
        tagwriter.write_tag2(51, self.end_angle)
        tagwriter.write_tag2(73, self.is_counter_clockwise)

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        self.center = ocs.transform_2d_vertex(self.center, elevation)
        self.start_angle = ocs.transform_deg_angle(self.start_angle)
        self.end_angle = ocs.transform_deg_angle(self.end_angle)


class EllipseEdge:
    EDGE_TYPE = "EllipseEdge"

    def __init__(self):
        self.center = Vec2((0., 0.))
        # Endpoint of major axis relative to center point (in OCS)
        self.major_axis = Vec2((1., 0.))
        self.ratio: float = 1.
        self.start_angle: float = 0.  # start param, not a real angle
        self.end_angle: float = 360.  # end param, not a real angle
        self.is_counter_clockwise: int = 0

    @classmethod
    def load_tags(cls, tags: Tags) -> 'EllipseEdge':
        edge = cls()
        for tag in tags:
            code, value = tag
            if code == 10:
                edge.center = Vec2(value)
            elif code == 11:
                edge.major_axis = Vec2(value)
            elif code == 40:
                edge.ratio = value
            elif code == 50:
                edge.start_angle = value
            elif code == 51:
                edge.end_angle = value
            elif code == 73:
                edge.is_counter_clockwise = value
        return edge

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(72, 3)  # edge type
        x, y, *_ = self.center
        tagwriter.write_tag2(10, float(x))
        tagwriter.write_tag2(20, float(y))
        x, y, *_ = self.major_axis
        tagwriter.write_tag2(11, float(x))
        tagwriter.write_tag2(21, float(y))
        tagwriter.write_tag2(40, self.ratio)
        tagwriter.write_tag2(50, self.start_angle)
        tagwriter.write_tag2(51, self.end_angle)
        tagwriter.write_tag2(73, self.is_counter_clockwise)

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        def adjust_angle(a: float, ratio: float) -> float:
            return math.atan2(math.sin(a) * ratio, math.cos(a))

        def adjust_param(p: float, ratio: float) -> float:
            return math.atan2(math.sin(p) / ratio, math.cos(p))
        # todo: start- and end param adjustment still incorrect for non-uniform scaling (axis transformation)
        ocs_to_wcs = ocs.old_ocs.to_wcs
        start_param = adjust_param(math.radians(self.start_angle), self.ratio)
        end_param = adjust_param(math.radians(self.end_angle), self.ratio)
        params = ellipse.Params(
            ocs_to_wcs(Vector(self.center).replace(z=elevation)),
            ocs_to_wcs(Vector(self.major_axis)),
            None,  # minor axis, not needed as input
            ocs.old_extrusion,
            self.ratio,
            start_param,
            end_param,
        )
        params = ellipse.transform(params, ocs.m)
        wcs_to_ocs = ocs.new_ocs.from_wcs
        self.center = wcs_to_ocs(params.center).vec2
        self.major_axis = wcs_to_ocs(params.major_axis).vec2
        self.ratio = params.ratio
        self.start_angle = math.degrees(adjust_angle(params.start, params.ratio))
        self.end_angle = math.degrees(adjust_angle(params.end, params.ratio))
        if ocs.new_extrusion.isclose(params.extrusion, abs_tol=1e-9):
            # ellipse extrusion matches new hatch extrusion
            pass
        elif ocs.new_extrusion.isclose(-params.extrusion, abs_tol=1e-9):
            # ellipse extrusion is opposite to new hatch extrusion
            self.is_counter_clockwise = 1 - int(self.is_counter_clockwise)
        else:
            raise ArithmeticError('Invalid EllipseEdge() transformation, please send bug report.')


class SplineEdge:
    EDGE_TYPE = "SplineEdge"

    def __init__(self):
        self.degree: int = 3  # code = 94
        self.rational: int = 0  # code = 73
        self.periodic: int = 0  # code = 74
        self.knot_values: List[float] = []
        self.control_points: List[Vec2] = []
        self.fit_points: List[Vec2] = []
        self.weights: List[float] = []
        # do not set tangents by default to (0, 0)
        self.start_tangent: Optional[Vec2] = None
        self.end_tangent: Optional[Vec2] = None

    @classmethod
    def load_tags(cls, tags: Tags) -> 'SplineEdge':
        edge = cls()
        for tag in tags:
            code, value = tag
            if code == 94:
                edge.degree = value
            elif code == 73:
                edge.rational = value
            elif code == 74:
                edge.periodic = value
            elif code == 40:
                edge.knot_values.append(value)
            elif code == 42:
                edge.weights.append(value)
            elif code == 10:
                edge.control_points.append(Vec2(value))
            elif code == 11:
                edge.fit_points.append(Vec2(value))
            elif code == 12:
                edge.start_tangent = Vec2(value)
            elif code == 13:
                edge.end_tangent = Vec2(value)
        return edge

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        write_tag = tagwriter.write_tag2
        write_tag(72, 4)  # edge type
        write_tag(94, int(self.degree))
        write_tag(73, int(self.rational))
        write_tag(74, int(self.periodic))
        write_tag(95, len(self.knot_values))  # number of knots
        write_tag(96, len(self.control_points))  # number of control points
        # build knot values list
        # knot values have to be present and valid, otherwise AutoCAD crashes
        if len(self.knot_values):
            for value in self.knot_values:
                write_tag(40, float(value))
        else:
            raise const.DXFValueError("SplineEdge: missing required knot values")

        # build control points
        # control points have to be present and valid, otherwise AutoCAD crashes
        for x, y, *_ in self.control_points:
            write_tag(10, float(x))
            write_tag(20, float(y))

        # build weights list, optional
        for value in self.weights:
            write_tag(42, float(value))

        # build fit points
        # fit points have to be present and valid, otherwise AutoCAD crashes
        # edit 2016-12-20: this is not true - there are examples with no fit points and without crashing AutoCAD
        if len(self.fit_points) > 0:
            write_tag(97, len(self.fit_points))
            for x, y, *_ in self.fit_points:
                write_tag(11, float(x))
                write_tag(21, float(y))
        elif tagwriter.dxfversion >= DXF2010:
            # (97, 0) len tag required by AutoCAD 2010+
            write_tag(97, 0)

        if self.start_tangent is not None:
            x, y, *_ = self.start_tangent
            write_tag(12, float(x))
            write_tag(22, float(y))

        if self.end_tangent is not None:
            x, y, *_ = self.end_tangent
            write_tag(13, float(x))
            write_tag(23, float(y))

    def transform(self, ocs: OCSTransform, elevation: float) -> None:
        self.control_points = list(ocs.transform_2d_vertex(v, elevation) for v in self.control_points)
        self.fit_points = list(ocs.transform_2d_vertex(v, elevation) for v in self.fit_points)
        if self.start_tangent is not None:
            t = Vector(self.start_tangent).replace(z=elevation)
            self.start_tangent = ocs.transform_direction(t).vec2
        if self.end_tangent is not None:
            t = Vector(self.end_tangent).replace(z=elevation)
            self.end_tangent = ocs.transform_direction(t).vec2


EDGE_CLASSES = [None, LineEdge, ArcEdge, EllipseEdge, SplineEdge]
EdgeTypes = Union[LineEdge, ArcEdge, EllipseEdge, SplineEdge]


class Pattern:
    def __init__(self, lines=None):
        self.lines = lines or []

    @classmethod
    def load_tags(cls, tags: Tags) -> 'Pattern':
        grouped_line_tags = group_tags(tags, splitcode=53)
        return cls([PatternLine.load_tags(line_tags) for line_tags in grouped_line_tags])

    def clear(self) -> None:
        """ Delete all pattern definition lines. """
        self.lines = []

    def add_line(self,
                 angle: float = 0.,
                 base_point: Tuple[float, float] = (0., 0.),
                 offset: Tuple[float, float] = (0., 0.),
                 dash_length_items: List[float] = None) -> None:
        """ Create a new pattern definition line and add the line to the :attr:`Pattern.lines` attribute. """
        self.lines.append(self.new_line(angle, base_point, offset, dash_length_items))

    @staticmethod
    def new_line(angle: float = 0.,
                 base_point: Tuple[float, float] = (0., 0.),
                 offset: Tuple[float, float] = (0., 0.),
                 dash_length_items: List[float] = None) -> 'PatternLine':
        """
        Create a new pattern definition line, but does not add the line to the :attr:`Pattern.lines` attribute.

        """
        if dash_length_items is None:
            raise const.DXFValueError("Parameter 'dash_length_items' must not be None.")
        return PatternLine(angle, base_point, offset, dash_length_items)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        if len(self.lines):
            tagwriter.write_tag2(78, len(self.lines))
            for line in self.lines:
                line.export_dxf(tagwriter)

    def __str__(self) -> str:
        return "[" + ",".join(str(line) for line in self.lines) + "]"

    def as_list(self) -> List:
        return [line.as_list() for line in self.lines]


class PatternLine:
    def __init__(self,
                 angle: float = 0.,
                 base_point: Tuple[float, float] = (0., 0.),
                 offset: Tuple[float, float] = (0., 0.),
                 dash_length_items: List[float] = None):
        self.angle = angle  # as always in degrees (circle = 360 deg)
        self.base_point = base_point
        self.offset = offset
        self.dash_length_items = [] if dash_length_items is None else dash_length_items  # type: List[float]
        # dash_length_items = [item0, item1, ...]
        # item > 0 is line, < 0 is gap, 0.0 = dot;

    @staticmethod
    def load_tags(tags: Tags) -> 'PatternLine':
        p = {53: 0, 43: 0, 44: 0, 45: 0, 46: 0}
        dash_length_items = []
        for tag in tags:
            code, value = tag
            if code == 49:
                dash_length_items.append(value)
            else:
                p[code] = value
        return PatternLine(p[53], (p[43], p[44]), (p[45], p[46]), dash_length_items)

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        write_tag = tagwriter.write_tag2
        write_tag(53, self.angle)
        write_tag(43, self.base_point[0])
        write_tag(44, self.base_point[1])
        write_tag(45, self.offset[0])
        write_tag(46, self.offset[1])
        write_tag(79, len(self.dash_length_items))
        for item in self.dash_length_items:
            write_tag(49, item)

    def __str__(self):
        return "[{0.angle}, {0.base_point}, {0.offset}, {0.dash_length_items}]".format(self)

    def as_list(self) -> List:
        return [self.angle, self.base_point, self.offset, self.dash_length_items]


class Gradient:
    def __init__(self):
        self.kind = 1  # 1 for gradient by default, 0 for Solid
        self.color1 = (0, 0, 0)  # type: RGB
        self.aci1 = None
        self.color2 = (255, 255, 255)  # type: RGB
        self.aci2 = None
        self.one_color = 0  # if 1 - a fill that uses a smooth transition between color1 and a specified tint
        self.rotation = 0.  # use grad NOT radians here, because there should be ONE system for all angles
        self.centered = 0.
        self.tint = 0.0
        self.name = 'LINEAR'

    @classmethod
    def load_tags(cls, tags: Tags) -> 'Gradient':
        gdata = cls()
        assert tags[0].code == 450
        gdata.kind = tags[0].value  # 0 for solid - 1 for gradient
        first_color_value = True
        first_aci_value = True
        for code, value in tags:
            if code == 460:
                gdata.rotation = math.degrees(value)  # radians to grad
            elif code == 461:
                gdata.centered = value
            elif code == 452:
                gdata.one_color = value
            elif code == 462:
                gdata.tint = value
            elif code == 470:
                gdata.name = value
            elif code == 63:
                if first_aci_value:
                    gdata.aci1 = value
                    first_aci_value = False
                else:
                    gdata.aci2 = value
            elif code == 421:
                if first_color_value:
                    gdata.color1 = int2rgb(value)
                    first_color_value = False
                else:
                    gdata.color2 = int2rgb(value)
        return gdata

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        # order matters!
        write_tag = tagwriter.write_tag2
        write_tag(450, self.kind)  # gradient or solid
        write_tag(451, 0)  # reserved for the future
        write_tag(460, math.radians(self.rotation))  # rotation angle in radians
        write_tag(461, self.centered)  # see DXF standard
        write_tag(452, self.one_color)  # one (1) or two (0) color gradient
        write_tag(462, self.tint)  # see DXF standard
        write_tag(453, 2)  # number of colors
        write_tag(463, 0)  # first value, see DXF standard
        if self.aci1 is not None:
            write_tag(63, self.aci1)
        # code == 63 "color as ACI" can be left off
        write_tag(421, rgb2int(self.color1))  # first color
        write_tag(463, 1)  # second value, see DXF standard
        if self.aci2 is not None:
            write_tag(63, self.aci2)  # code 63 "color as ACI" could be left off
        write_tag(421, rgb2int(self.color2))  # second color
        write_tag(470, self.name)
