# Copyright (c) 2019 Manfred Moitzi
# License: MIT License
# Created 2019-03-08
from typing import TYPE_CHECKING, List, Tuple, Union, Sequence, Iterable, Optional
from contextlib import contextmanager
import math
import copy
from ezdxf.math import Vector
from ezdxf.tools.rgb import rgb2int, int2rgb
from ezdxf.tools.pattern import PATTERN  # acad standard pattern definitions
from ezdxf.lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass, XType
from ezdxf.lldxf.tags import Tags, group_tags
from ezdxf.lldxf.const import SUBCLASS_MARKER, DXF2000, DXF2004
from ezdxf.lldxf import const
from ezdxf.math.bspline import bspline_control_frame
from .dxfentity import base_class, SubclassProcessor
from .dxfgfx import DXFGraphic, acdb_entity
from .factory import register_entity

if TYPE_CHECKING:
    from ezdxf.eztypes2 import TagWriter, DXFNamespace, Drawing, RGB

__all__ = ['Hatch', 'Gradient', 'Pattern']

acdb_hatch = DefSubclass('AcDbHatch', {
    # 3D point (X and Y always equal 0, Z represents the elevation)
    'elevation': DXFAttr(10, xtype=XType.point3d, default=Vector(0, 0, 0)),  # OCS

    # Extrusion direction (optional; default = 0, 0, 1)
    'extrusion': DXFAttr(210, xtype=XType.point3d, default=Vector(0, 0, 1), optional=True),

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
    'hatch_style': DXFAttr(75, default=const.HATCH_STYLE_OUTERMOST),

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
    'n_seed_points': DXFAttr(98),  # number of seed points
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
    MIN_DXF_VERSION_FOR_EXPORT = DXF2000

    def __init__(self, doc: 'Drawing' = None):
        super().__init__(doc)
        self.loops = BoundaryPaths()
        self.pattern = None  # type: Pattern
        self.gradient = None  # type: Gradient
        self.seeds = []

    def _copy_data(self, entity: 'Hatch') -> None:
        """ Copy loops, pattern, gradient, seeds. """
        entity.loops = copy.deepcopy(self.loops)
        entity.pattern = copy.deepcopy(self.pattern)
        entity.gradient = copy.deepcopy(self.gradient)
        entity.seeds = copy.deepcopy(self.seeds)

    def load_dxf_attribs(self, processor: SubclassProcessor = None) -> 'DXFNamespace':
        dxf = super().load_dxf_attribs(processor)
        if processor:
            tags = Tags(processor.subclasses[2][1:])  # copy without subclass marker
            tags = self.load_loops(tags)  # removes loop data from tags
            tags = self.load_gradient(tags)  # removes gradient data
            tags = self.load_pattern(tags)  # removes pattern tags
            tags = self.load_seeds(tags)  # removes seed tags

            # load HATCH DXF attributes from remaining tags
            tags = processor.load_tags_into_namespace(dxf, tags, acdb_hatch)
            if len(tags):
                processor.log_unprocessed_tags(tags, subclass=acdb_hatch.name)
        return dxf

    def load_loops(self, tags: Tags) -> Tags:
        # find first group code 91 = count of loops, Spline data also contains group code 91!
        try:
            start_index = tags.tag_index(91)
        except const.DXFValueError:
            raise const.DXFStructureError(
                "HATCH: Missing required DXF tag 'Number of boundary paths (loops)' (code=91).")

        loop_tags = tags.collect_consecutive_tags(PATH_CODES, start=start_index)
        if len(loop_tags):
            self.loops = BoundaryPaths.load_tags(loop_tags)
        end_index = start_index + len(loop_tags) + 1
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
        del tags[index: index + len(pattern_tags) + 2]
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
        self.loops.export_dxf(tagwriter)
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
        return bool(self.dxf.solid_fill)

    @property
    def has_pattern_fill(self) -> bool:
        return not bool(self.dxf.solid_fill)

    @property
    def has_gradient_data(self) -> bool:
        return bool(self.gradient)

    @property
    def bgcolor(self) -> Optional['RGB']:
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

        yield self.loops

    def set_solid_fill(self, color: int = 7, style: int = 1, rgb: 'RGB' = None):
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

    def set_gradient(self,
                     color1: 'RGB' = (0, 0, 0),
                     color2: 'RGB' = (255, 255, 255),
                     rotation: float = 0.,
                     centered: float = 0.,
                     one_color: int = 0,
                     tint: float = 0.,
                     name: str = 'LINEAR') -> None:
        if self.doc is not None and self.drawing.dxfversion < DXF2004:
            raise const.DXFVersionError("Gradient support requires at least DXF R2004")
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
        if not self.gradient:
            raise const.DXFValueError('HATCH has no gradient data.')
        yield self.gradient

    def set_pattern_fill(self, name: str, color: int = 7, angle: float = 0., scale: float = 1., double: int = 0,
                         style: int = 1, pattern_type: int = 1, definition=None) -> None:
        self.gradient = None
        self.dxf.solid_fill = 0
        self.dxf.pattern_name = name
        self.dxf.color = color
        self.dxf.hatch_style = style
        self.dxf.pattern_type = pattern_type

        if definition is None:
            # get pattern definition from acad standard pattern, default is 'ANSI31'
            definition = PATTERN.get(name, PATTERN['ANSI31'])
        self.set_pattern_definition(definition)

    # just for compatibility
    @contextmanager
    def edit_pattern(self) -> 'Pattern':
        if not self.pattern:
            raise const.DXFValueError('Solid fill HATCH has no pattern data.')
        yield self.pattern

    def set_pattern_definition(self, lines: Sequence) -> None:
        """
        Setup hatch patten definition by a list of definition lines and  a definition line is a 4-tuple [angle,
        base_point, offset, dash_length_items]

            - angle: line angle in degrees
            - base-point: 2-tuple (x, y)
            - offset: 2-tuple (dx, dy)
            - dash_length_items: list of dash items (item > 0 is a line, item < 0 is a gap and item == 0.0 is a point)

        Args:
            lines: list of definition lines

        """
        self.pattern.lines = [PatternLine(line[0], line[1], line[2], line[3]) for line in lines]

    def get_seed_points(self) -> List:
        return self.seeds

    def set_seed_points(self, points: Sequence[Tuple[float, float]]) -> None:
        if len(points) < 1:
            raise const.DXFValueError(
                "Param points should be a collection of 2D points and requires at least one point.")
        self.seeds = list(points)


TPath = Union['PolylinePath', 'EdgePath']


class BoundaryPaths:
    def __init__(self, paths: List[TPath] = None):
        self.paths = paths or []  # type: List[TPath]

    @classmethod
    def load_tags(cls, tags: Tags) -> 'BoundaryPaths':
        paths = []
        assert tags[0].code == 91
        grouped_path_tags = group_tags(tags[1:], splitcode=92)
        for path_tags in grouped_path_tags:
            path_type_flags = path_tags[0].value
            is_polyline_path = bool(path_type_flags & 2)
            path = PolylinePath.load_tags(path_tags) if is_polyline_path else EdgePath.load_tags(path_tags)
            path.path_type_flags = path_type_flags
            paths.append(path)
        return cls(paths)

    def clear(self) -> None:
        self.paths = []

    def add_polyline_path(self, path_vertices: Sequence[Tuple[float, float]], is_closed: bool = True,
                          flags: int = 1) -> 'PolylinePath':
        new_path = PolylinePath()
        new_path.set_vertices(path_vertices, is_closed)
        new_path.path_type_flags = flags | const.BOUNDARY_PATH_POLYLINE
        self.paths.append(new_path)
        return new_path

    def add_edge_path(self, flags: int = 1) -> 'EdgePath':
        new_path = EdgePath()
        new_path.path_type_flags = flags
        self.paths.append(new_path)
        return new_path

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(91, len(self.paths))
        for path in self.paths:
            path.export_dxf(tagwriter)


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
        self.path_type_flags = const.BOUNDARY_PATH_POLYLINE
        self.is_closed = False
        self.vertices = []  # type: List[Tuple[float, float, float]]  # list of 2D coordinates with bulge values (x, y, bulge); bulge default = 0.0
        self.source_boundary_objects = []  # type: List[str]  # (330, handle) tags

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
            write_tag(10, (float(x), float(y)))
            if has_bulge:
                write_tag(42, float(bulge))

        export_source_boundary_objects(tagwriter, self.source_boundary_objects)


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

    def add_line(self, start: int, end: int) -> 'LineEdge':
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
                   periodic: int = 0) -> 'SplineEdge':
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
        self.edges = []

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(92, int(self.path_type_flags))
        tagwriter.write_tag2(93, len(self.edges))
        for edge in self.edges:
            edge.export_dxf(tagwriter)
        export_source_boundary_objects(tagwriter, self.source_boundary_objects)


class LineEdge:
    EDGE_TYPE = "LineEdge"

    def __init__(self):
        self.start = (0, 0)  # type: Tuple[float, float]
        self.end = (0, 0)  # type: Tuple[float, float]

    @classmethod
    def load_tags(cls, tags: Tags) -> 'LineEdge':
        edge = cls()
        for tag in tags:
            code, value = tag
            if code == 10:
                edge.start = Vector(value)
            elif code == 11:
                edge.end = Vector(value)
        return edge

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        tagwriter.write_tag2(72, 1)  # edge type
        tagwriter.write_vertex(10, self.start)
        tagwriter.write_vertex(11, self.end)


class ArcEdge:
    EDGE_TYPE = "ArcEdge"

    def __init__(self):
        self.center = (0., 0.)  # type: Tuple[float, float]
        self.radius = 1.
        self.start_angle = 0.
        self.end_angle = 360.
        self.is_counter_clockwise = 0

    @classmethod
    def load_tags(cls, tags: Tags) -> 'ArcEdge':
        edge = cls()
        for tag in tags:
            code, value = tag
            if code == 10:
                edge.center = value
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
        tagwriter.write_vertex(10, self.center)
        tagwriter.write_tag2(40, self.radius)
        tagwriter.write_tag2(50, self.start_angle)
        tagwriter.write_tag2(51, self.end_angle)
        tagwriter.write_tag2(73, self.is_counter_clockwise)


class EllipseEdge:
    EDGE_TYPE = "EllipseEdge"

    def __init__(self):
        self.center = (0., 0.)  # type: Tuple[float, float]
        # Endpoint of major axis relative to center point (in OCS)
        self.major_axis = (1., 0.)  # type: Tuple[float, float]
        self.ratio = 1.
        self.start_angle = 0.
        self.end_angle = 360.
        self.is_counter_clockwise = 0

    @classmethod
    def load_tags(cls, tags: Tags) -> 'EllipseEdge':
        edge = cls()
        for tag in tags:
            code, value = tag
            if code == 10:
                edge.center = value
            elif code == 11:
                edge.major_axis = value
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
        tagwriter.write_vertex(10, self.center)
        tagwriter.write_vertex(11, self.major_axis)
        tagwriter.write_tag2(40, self.ratio)
        tagwriter.write_tag2(50, self.start_angle)
        tagwriter.write_tag2(51, self.end_angle)
        tagwriter.write_tag2(73, self.is_counter_clockwise)


class SplineEdge:
    EDGE_TYPE = "SplineEdge"

    def __init__(self):
        self.degree = 3  # code = 94
        self.rational = 0  # code = 73
        self.periodic = 0  # code = 74
        self.knot_values = []  # type: List[float]
        self.control_points = []  # type: List[Tuple[float, float]]
        self.fit_points = []  # type: List[Tuple[float, float]]
        self.weights = []  # type: List[float]
        self.start_tangent = (0, 0)  # type: Tuple[float, float]
        self.end_tangent = (0, 0)  # type: Tuple[float, float]

    @classmethod
    def from_tags(cls, tags: Tags) -> 'SplineEdge':
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
                edge.control_points.append(value)
            elif code == 11:
                edge.fit_points.append(value)
            elif code == 12:
                edge.start_tangent = value
            elif code == 13:
                edge.end_tangent = value
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
        for value in self.control_points:
            tagwriter.write_vertex(10, (float(value[0]), float(value[1])))

        # build weights list, optional
        for value in self.weights:
            write_tag(42, float(value))

        # build fit points
        # fit points have to be present and valid, otherwise AutoCAD crashes
        # edit 2016-12-20: this is not true - there are examples with no fit points and without crashing AutoCAD
        write_tag(97, len(self.fit_points))
        for value in self.fit_points:
            tagwriter.write_vertex(11, (float(value[0]), float(value[1])))

        tagwriter.write_vertex(12, (float(self.start_tangent[0]), float(self.start_tangent[1])))
        tagwriter.write_vertex(13, (float(self.end_tangent[0]), float(self.end_tangent[1])))


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
        self.lines = []

    def add_line(self,
                 angle: float = 0.,
                 base_point: Tuple[float, float] = (0., 0.),
                 offset: Tuple[float, float] = (0., 0.),
                 dash_length_items: List[float] = None) -> None:
        self.lines.append(self.new_line(angle, base_point, offset, dash_length_items))

    @staticmethod
    def new_line(angle: float = 0.,
                 base_point: Tuple[float, float] = (0., 0.),
                 offset: Tuple[float, float] = (0., 0.),
                 dash_length_items: List[float] = None) -> 'PatternLine':
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


class Gradient:
    def __init__(self):
        self.color1 = (0, 0, 0)  # type: RGB
        self.color2 = (255, 255, 255)  # type: RGB
        self.one_color = 0  # if 1 - a fill that uses a smooth transition between color1 and a specified tint
        self.rotation = 0.  # use grad NOT radians here, because there should be ONE system for all angles
        self.centered = 0.
        self.tint = 0.0
        self.name = 'LINEAR'

    @classmethod
    def load_tags(cls, tags: Tags) -> 'Gradient':
        gdata = cls()
        assert tags[0].code == 450
        # if tags[0].value == 0 hatch is a solid ????
        first_color_value = True
        for code, value in tags:
            if code == 460:
                gdata.rotation = (value / math.pi) * 180.  # radians to grad
            elif code == 461:
                gdata.centered = value
            elif code == 452:
                gdata.one_color = value
            elif code == 462:
                gdata.tint = value
            elif code == 470:
                gdata.name = value
            elif code == 421:
                # code == 63 color as ACI, can be ignored
                if first_color_value:
                    gdata.color1 = int2rgb(value)
                    first_color_value = False
                else:
                    gdata.color2 = int2rgb(value)
        return gdata

    def export_dxf(self, tagwriter: 'TagWriter') -> None:
        write_tag = tagwriter.write_tag2
        write_tag(450, 1)  # gradient
        write_tag(451, 0)  # reserved for the future
        write_tag(452, self.one_color)  # one (1) or two (0) color gradient
        write_tag(453, 2)  # number of colors
        write_tag(460, (self.rotation / 180.) * math.pi)  # rotation angle in radians
        write_tag(461, self.centered)  # see DXF standard
        write_tag(462, self.tint)  # see DXF standard
        write_tag(463, 0)  # first value, see DXF standard
        # code == 63 "color as ACI" can be left off
        write_tag(421, rgb2int(self.color1))  # first color
        write_tag(463, 1)  # second value, see DXF standard
        #  code 63 "color as ACI" can be left off
        write_tag(421, rgb2int(self.color2))  # second color
        write_tag(470, self.name)
