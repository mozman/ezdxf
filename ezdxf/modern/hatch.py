# Created: 24.05.2015
# Copyright (c) 2015-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
import math
from contextlib import contextmanager
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..lldxf.attributes import DXFAttr, DXFAttributes, DefSubclass
from ..lldxf.types import DXFTag, DXFVertex
from ..lldxf.tags import DXFStructureError, group_tags, Tags
from ..lldxf.extendedtags import ExtendedTags
from ..lldxf import const
from ..tools.pattern import PATTERN  # acad standard pattern definitions
from ..tools.rgb import rgb2int, int2rgb
from ..lldxf.const import DXFValueError, DXFVersionError

_HATCH_TPL = """0
HATCH
5
0
330
0
100
AcDbEntity
8
0
62
1
100
AcDbHatch
10
0.0
20
0.0
30
0.0
210
0.0
220
0.0
230
1.0
2
SOLID
70
1
71
0
91
0
75
1
76
1
98
1
10
0.0
20
0.0
"""

# removed tag (code=47, 0.0442352806926743) from Template: pixel size - caused problems in AutoCAD

# default is a solid fil hatch
hatch_subclass = DefSubclass('AcDbHatch', {
    'elevation': DXFAttr(10, xtype='Point3D', default=(0.0, 0.0, 0.0)),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
    'pattern_name': DXFAttr(2, default='SOLID'),  # for solid fill
    'solid_fill': DXFAttr(70, default=1),  # pattern fill = 0
    'associative': DXFAttr(71, default=0),  # associative flag = 0
    'hatch_style': DXFAttr(75, default=const.HATCH_STYLE_OUTERMOST),  # 0=normal; 1=outer; 2=ignore
    'pattern_type': DXFAttr(76, default=const.HATCH_TYPE_PREDEFINED),  # 0=user; 1=predefined; 2=custom???
    'pattern_angle': DXFAttr(52, default=0.0),  # degrees (360deg = circle)
    'pattern_scale': DXFAttr(41, default=1.0),
    'pattern_double': DXFAttr(77, default=0),  # 0=not double; 1= double
    'n_seed_points': DXFAttr(98),  # number of seed points
})

GRADIENT_CODES = frozenset([450, 451, 452, 453, 460, 461, 462, 463, 470, 421, 63])
PATH_CODES = frozenset([10, 11, 12, 13, 40, 42, 50, 51, 42, 72, 73, 74, 92, 93, 94, 95, 96, 97, 330])
PATTERN_DEFINITION_LINE_CODES = frozenset((53, 43, 44, 45, 46, 79, 49))


class Hatch(ModernGraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_HATCH_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, hatch_subclass)

    @property
    def AcDbHatch(self):
        return self.tags.subclasses[2]

    @property
    def has_solid_fill(self):
        return bool(self.dxf.solid_fill)

    @property
    def has_pattern_fill(self):
        return not bool(self.dxf.solid_fill)

    @property
    def has_gradient_data(self):
        return bool(self.AcDbHatch.get_first_value(450, 0))

    @property
    def bgcolor(self):
        try:
            xdata_bgcolor = self.tags.get_xdata('HATCHBACKGROUNDCOLOR')
        except ValueError:
            return None
        color = xdata_bgcolor.get_first_value(1071, 0)
        return int2rgb(color)

    @bgcolor.setter
    def bgcolor(self, rgb):
        color_value = rgb2int(rgb) | -0b111110000000000000000000000000  # it's magic
        try:
            xdata_bgcolor = self.tags.get_xdata('HATCHBACKGROUNDCOLOR')
        except DXFValueError:  # no xdata for background color found
            self.tags.xdata.append(Tags([
                DXFTag(1001, 'HATCHBACKGROUNDCOLOR'),
                DXFTag(1071, color_value),
            ]))
        else:
            xdata_bgcolor.set_first(DXFTag(1071, color_value))

    @bgcolor.deleter
    def bgcolor(self):
        try:
            xdata_bgcolor = self.tags.get_xdata('HATCHBACKGROUNDCOLOR')
        except DXFValueError:  # background color does not exist
            return
        else:
            self.tags.xdata.remove(xdata_bgcolor)

    @contextmanager
    def edit_boundary(self):
        boundary_path_data = BoundaryPathData(self)
        yield boundary_path_data
        self._set_boundary_path_data(boundary_path_data)

    def _set_boundary_path_data(self, boundary_path_data):
        # replace existing path tags by the new path
        start_index = boundary_path_data.start_index
        end_index = boundary_path_data.end_index
        self.AcDbHatch[start_index: end_index] = boundary_path_data.dxftags()

    def set_solid_fill(self, color=7, style=1, rgb=None):
        self._remove_gradient_data()
        if self.has_pattern_fill:
            self._remove_pattern_data()
            self.dxf.solid_fill = 1

        self.dxf.color = color  # if a rgb value is present, the color value is ignored by AutoCAD
        self.dxf.hatch_style = style
        self.dxf.pattern_name = 'SOLID'
        self.dxf.pattern_type = const.HATCH_TYPE_PREDEFINED
        if rgb is not None:  # if a rgb value is present, the color value is ignored by AutoCAD
            self.rgb = rgb  # rgb should be a (r, g, b) tuple

    def _remove_pattern_data(self):
        if self.has_pattern_fill:
            with self.edit_pattern() as e:  # delete existing pattern definition
                e.clear()
            self.AcDbHatch.remove_tags((52, 41, 77))
            # Important: AutoCAD does not allow the tags pattern_angle (52), pattern_scale (41), pattern_double (77) for
            # hatches with SOLID fill.

    def set_gradient(self, color1=(0, 0, 0), color2=(255, 255, 255), rotation=0., centered=0., one_color=0, tint=0.,
                     name='LINEAR'):
        if self.drawing is not None and self.drawing.dxfversion < 'AC1018':
            raise DXFVersionError("Gradient support requires at least DXF version AC1018, this drawing is:%s" % self.drawing.dxfversion)
        gradient_data = GradientData()
        gradient_data.color1 = color1
        gradient_data.color2 = color2
        gradient_data.one_color = one_color
        gradient_data.rotation = rotation
        gradient_data.centered = centered
        gradient_data.tint = tint
        gradient_data.name = name
        self._set_gradient(gradient_data)

    def get_gradient(self):
        if not self.has_gradient_data:
            raise DXFValueError('HATCH has no gradient data.')
        return GradientData.from_tags(self.AcDbHatch)

    def _set_gradient(self, gradient_data):
        gradient_data.name = gradient_data.name.upper()
        if gradient_data.name not in const.GRADIENT_TYPES:
            raise DXFValueError('Invalid gradient type name: %s' % gradient_data.name)

        self._remove_pattern_data()
        self._remove_gradient_data()
        self.dxf.solid_fill = 1
        self.dxf.pattern_name = 'SOLID'
        self.dxf.pattern_type = const.HATCH_TYPE_PREDEFINED
        self.AcDbHatch.extend(gradient_data.dxftags())

    def _remove_gradient_data(self):
        self.AcDbHatch.remove_tags(GRADIENT_CODES)

    @contextmanager
    def edit_gradient(self):
        if not self.has_gradient_data:
            raise DXFValueError('HATCH has no gradient data.')
        gradient_data = GradientData.from_tags(self.AcDbHatch)
        yield gradient_data
        self._set_gradient(gradient_data)

    def set_pattern_fill(self, name, color=7, angle=0., scale=1., double=0, style=1, pattern_type=1, definition=None):
        self._remove_gradient_data()
        self.dxf.solid_fill = 0
        self.dxf.pattern_name = name
        self.dxf.color = color
        self.dxf.hatch_style = style
        self.dxf.pattern_type = pattern_type

        # safe version of adding pattern fill specific DXF tags:
        self.AcDbHatch.remove_tags((52, 41, 77))  # remove pattern angle, pattern scale & pattern double flag if exists
        try:
            index = self.AcDbHatch.tag_index(76) + 1  # find position of pattern type (76); + 1: insert after tag 76
        except DXFValueError:
            raise DXFStructureError("HATCH: Missing required DXF tag 'Hatch pattern type' (code=76).")
        # insert pattern angle, pattern scale & pattern double flag behind pattern type
        self.AcDbHatch[index:index] = [DXFTag(52, angle), DXFTag(41, scale), DXFTag(77, double)]
        # place pattern definition right behind pattern double flag (77)
        if definition is None:
            # get pattern definition from acad standard pattern, default is 'ANSI31'
            definition = PATTERN.get(name, PATTERN['ANSI31'])
        self.set_pattern_definition(definition)

    @contextmanager
    def edit_pattern(self):
        if self.has_solid_fill:
            raise DXFValueError('Solid fill HATCH has no pattern data.')
        pattern_data = PatternData(self)
        yield pattern_data
        self._set_pattern_data(pattern_data)

    def _set_pattern_data(self, new_pattern_data):
        start_index = new_pattern_data.existing_pattern_start_index
        end_index = new_pattern_data.existing_pattern_end_index
        pattern_tags = new_pattern_data.dxftags()
        if start_index == 0:  # no existing pattern data
            try:
                start_index = self.AcDbHatch.tag_index(77) + 1  # hatch pattern double flag, used as insertion point
                end_index = start_index
            except DXFValueError:
                raise DXFStructureError("HATCH: Missing required DXF tag 'Hatch pattern double flag' (code=77).")
        # replace existing pattern data
        self.AcDbHatch[start_index: end_index] = pattern_tags

    def set_pattern_definition(self, lines):
        """
        Setup hatch patten definition by a list of definition lines and  a definition line is a 4-tuple [angle,
        base_point, offset, dash_length_items]

        - angle: line angle in degrees
        - base-point: 2-tuple (x, y)
        - offset: 2-tuple (dx, dy)
        - dash_length_items: list of dash items (item > 0 is a line, item < 0 is a gap and item == 0.0 is a point)

        :param lines: list of definition lines
        """
        pattern_lines = [PatternDefinitionLine(line[0], line[1], line[2], line[3]) for line in lines]
        with self.edit_pattern() as pattern_editor:
            pattern_editor.lines = pattern_lines

    def get_seed_points(self):
        hatch_tags = self.AcDbHatch
        first_seed_point_index = self._get_seed_point_index(hatch_tags)
        seed_points = hatch_tags.collect_consecutive_tags([10], start=first_seed_point_index)
        return [tag.value for tag in seed_points]

    def _get_seed_point_index(self, hatch_tags):
        try:
            seed_count_index = hatch_tags.tag_index(98)  # find index of 'Number of seed points'
        except DXFValueError:
            raise DXFStructureError("HATCH: Missing required DXF tag 'Number of seed points' (code=98).")
        try:
            first_seed_point_index = hatch_tags.tag_index(10, seed_count_index+1)
        except DXFValueError:
            raise DXFStructureError("HATCH: Missing required DXF tags 'seed point X value' (code=10).")
        return first_seed_point_index

    def set_seed_points(self, points):
        if len(points) < 1:
            raise DXFValueError("Param points should be a collection of 2D points and requires at least one point.")
        hatch_tags = self.AcDbHatch
        first_seed_point_index = self._get_seed_point_index(hatch_tags)
        existing_seed_points = hatch_tags.collect_consecutive_tags([10], start=first_seed_point_index)  # don't rely on 'Number of seed points'
        new_seed_points = [DXFVertex(10, (point[0], point[1])) for point in points]  # only use x and y coordinate,
        self.dxf.n_seed_points = len(new_seed_points)  # set new count of seed points
        # replace existing seed points
        hatch_tags[first_seed_point_index: first_seed_point_index+len(existing_seed_points)] = new_seed_points


class BoundaryPathData(object):
    def __init__(self, hatch):
        self.start_index = 0
        self.end_index = 0
        self.paths = self._setup_paths(hatch.AcDbHatch)

    def _setup_paths(self, tags):
        paths = []
        try:
            self.start_index = tags.tag_index(91)  # code 91=Number of boundary paths (loops)
            n_paths = tags[self.start_index].value
        except DXFValueError:
            raise DXFStructureError("HATCH: Missing required DXF tag 'Number of boundary paths (loops)' (code=91).")

        self.end_index = self.start_index + 1  # + 1 for Tag(91, Number of boundary paths)
        if n_paths == 0:  # created by ezdxf from template without path data
            return paths

        all_path_tags = tags.collect_consecutive_tags(PATH_CODES, start=self.start_index+1)
        self.end_index = self.start_index + len(all_path_tags) + 1  # + 1 for Tag(91, Number of boundary paths)
        # end_index: stored for Hatch._set_boundary_path_data()
        grouped_path_tags = group_tags(all_path_tags, splitcode=92)
        for path_tags in grouped_path_tags:
            path_type_flags = path_tags[0].value
            is_polyline_path = bool(path_type_flags & 2)
            path = PolylinePath.from_tags(path_tags) if is_polyline_path else EdgePath.from_tags(path_tags)
            path.path_type_flags = path_type_flags
            paths.append(path)
        return paths

    def clear(self):
        self.paths = []

    def add_polyline_path(self, path_vertices, is_closed=1, flags=1):
        new_path = PolylinePath()
        new_path.set_vertices(path_vertices, is_closed)
        new_path.path_type_flags = flags | const.BOUNDARY_PATH_POLYLINE
        self.paths.append(new_path)
        return new_path

    def add_edge_path(self, flags=1):
        new_path = EdgePath()
        new_path.path_type_flags = flags
        self.paths.append(new_path)
        return new_path

    def dxftags(self):
        tags = [DXFTag(91, len(self.paths))]
        for path in self.paths:
            tags.extend(path.dxftags())
        return tags


def pop_source_boundary_objects_tags(all_path_tags):
    source_boundary_object_tags = []
    while len(all_path_tags):
        if all_path_tags[-1].code in (97, 333):
            last_tag = all_path_tags.pop()
            if last_tag.code == 330:
                source_boundary_object_tags.append(last_tag)
            else:  # code == 97
                # result list does not contain the length tag!
                source_boundary_object_tags.reverse()
                return source_boundary_object_tags
        else:
            return []  # no source boundary objects found - entity is not valid for AutoCAD


def build_source_boundary_object_tags(source_boundary_objects):
    source_boundary_object_tags = [DXFTag(97, len(source_boundary_objects))]
    source_boundary_object_tags.extend(source_boundary_objects)
    return source_boundary_object_tags


class PolylinePath(object):
    PATH_TYPE = 'PolylinePath'

    def __init__(self):
        self.path_type_flags = const.BOUNDARY_PATH_POLYLINE
        self.is_closed = 0
        self.vertices = []  # list of 2D coordinates with bulge values (x, y, bulge); bulge default = 0.0
        self.source_boundary_objects = []

    @staticmethod
    def from_tags(tags):
        polyline_path = PolylinePath()
        polyline_path._setup_path(tags)
        return polyline_path

    def _setup_path(self, tags):
        self.source_boundary_objects = pop_source_boundary_objects_tags(tags)
        for tag in tags:
            code, value = tag
            if code == 10:  # vertex coordinates
                self.vertices.append((value[0], value[1], 0.0))  # (x, y, bulge); bulge default = 0.0
            elif code == 42:  # bulge value
                x, y, bulge = self.vertices.pop()  # last value
                self.vertices.append((x, y, value))  # last coordinates with new bulge value
            elif code == 72:
                pass  # ignore this value
            elif code == 73:
                self.is_closed = value
            elif code == 92:
                self.path_type_flags = value
            elif code == 93:  # number of polyline vertices
                pass  # ignore this value

    def set_vertices(self, vertices, is_closed=1):
        new_vertices = []
        has_bulge = 0
        for vertex in vertices:
            if len(vertex) == 2:
                x, y = vertex
                bulge = 0
            elif len(vertex) == 3:
                x, y, bulge = vertex
            else:
                raise DXFValueError("Invalid vertex format, expected (x, y) or (x, y, bulge)")
            new_vertices.append((x, y, bulge))
        self.vertices = new_vertices
        self.is_closed = is_closed

    def clear(self):
        self.vertices = []
        self.is_closed = 0
        self.source_boundary_objects = []

    def has_bulge(self):
        for x, y, bulge in self.vertices:
            if bulge != 0:
                return True
        return False

    def dxftags(self):
        has_bulge = self.has_bulge()

        vtags = []
        for x, y, bulge in self.vertices:
            vtags.append(DXFVertex(10, (float(x), float(y))))
            if has_bulge:
                vtags.append(DXFTag(42, float(bulge)))

        tags = [
            DXFTag(92, int(self.path_type_flags)),
            DXFTag(72, int(has_bulge)),
            DXFTag(73, int(self.is_closed)),
            DXFTag(93, len(self.vertices)),
        ]
        tags.extend(vtags)
        tags.extend(build_source_boundary_object_tags(self.source_boundary_objects))
        return tags


class EdgePath(object):
    PATH_TYPE = 'EdgePath'

    def __init__(self):
        self.path_type_flags = const.BOUNDARY_PATH_DEFAULT
        self.edges = []
        self.source_boundary_objects = []

    @staticmethod
    def from_tags(tags):
        edge_path = EdgePath()
        edge_path._setup_path(tags)
        return edge_path

    def _setup_path(self, tags):
        self.source_boundary_objects = pop_source_boundary_objects_tags(tags)
        edge_groups = group_tags(tags, splitcode=72)
        for edge_tags in edge_groups:
            self.edges.append(self._setup_edge(edge_tags))

    def _setup_edge(self, tags):
        edge_type = tags[0].value
        if 0 < edge_type < 5:
            return EDGE_CLASSES[edge_type].from_tags(tags[1:])
        else:
            raise DXFStructureError("HATCH: unknown edge type: {}".format(edge_type))

    def add_line(self, start, end):
        line = LineEdge()
        line.start = start
        line.end = end
        self.edges.append(line)
        return line

    def add_arc(self, center, radius=1., start_angle=0., end_angle=360., is_counter_clockwise=0):
        arc = ArcEdge()
        arc.center = center
        arc.radius = radius
        arc.start_angle = start_angle
        arc.end_angle = end_angle
        arc.is_counter_clockwise = 1 if bool(is_counter_clockwise) else 0
        self.edges.append(arc)
        return arc

    def add_ellipse(self, center, major_axis=(1., 0.), ratio=1.,
                    start_angle=0., end_angle=360., is_counter_clockwise=0):
        if ratio > 1.:
            raise DXFValueError("Parameter 'ratio' has to be <= 1.0")
        ellipse = EllipseEdge()
        ellipse.center = center
        ellipse.major_axis = major_axis
        ellipse.ratio = ratio
        ellipse.start_angle = start_angle
        ellipse.end_angle = end_angle
        ellipse.is_counter_clockwise = is_counter_clockwise
        self.edges.append(ellipse)
        return ellipse

    def add_spline(self, fit_points=None, control_points=None, knot_values=None, weights=None, degree=3, rational=0, periodic=0):
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

    def clear(self):
        self.edges = []

    def dxftags(self):
        tags = [DXFTag(92, int(self.path_type_flags)), DXFTag(93, len(self.edges))]
        for edge in self.edges:
            tags.extend(edge.dxftags())
        tags.extend(build_source_boundary_object_tags(self.source_boundary_objects))
        return tags


class LineEdge(object):
    EDGE_TYPE = "LineEdge"
    # more struct than object

    def __init__(self):
        self.start = (0, 0)
        self.end = (0, 0)

    @staticmethod
    def from_tags(tags):
        edge = LineEdge()
        for tag in tags:
            code, value = tag
            if code == 10:
                edge.start = value
            elif code == 11:
                edge.end = value
        return edge

    def dxftags(self):
        return [
            DXFTag(72, 1),  # edge type
            DXFVertex(10, self.start),
            DXFVertex(11, self.end),
        ]


class ArcEdge(object):
    EDGE_TYPE = "ArcEdge"
    # more struct than object

    def __init__(self):
        self.center = (0., 0.)
        self.radius = 1.
        self.start_angle = 0.
        self.end_angle = 360.
        self.is_counter_clockwise = 0

    @staticmethod
    def from_tags(tags):
        edge = ArcEdge()
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

    def dxftags(self):
        return [
            DXFTag(72, 2),  # edge type
            DXFVertex(10, self.center),
            DXFTag(40, self.radius),
            DXFTag(50, self.start_angle),
            DXFTag(51, self.end_angle),
            DXFTag(73, self.is_counter_clockwise),
        ]


class EllipseEdge(object):
    EDGE_TYPE = "EllipseEdge"
    # more struct than object

    def __init__(self):
        self.center = (0., 0.)
        self.major_axis = (1., 0.)  # Endpoint of major axis relative to center point (in OCS)
        self.ratio = 1.
        self.start_angle = 0.
        self.end_angle = 360.
        self.is_counter_clockwise = 0

    @staticmethod
    def from_tags(tags):
        edge = EllipseEdge()
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

    def dxftags(self):
        return [
            DXFTag(72, 3),  # edge type
            DXFVertex(10, self.center),
            DXFVertex(11, self.major_axis),
            DXFTag(40, self.ratio),
            DXFTag(50, self.start_angle),
            DXFTag(51, self.end_angle),
            DXFTag(73, self.is_counter_clockwise)
        ]


class SplineEdge(object):
    EDGE_TYPE = "SplineEdge"

    def __init__(self):
        self.degree = 3  # code = 94
        self.rational = 0  # code = 73
        self.periodic = 0  # code = 74
        self.knot_values = []
        self.control_points = []
        self.fit_points = []
        self.weights = []
        self.start_tangent = (0, 0)
        self.end_tangent = (0, 0)

    @staticmethod
    def from_tags(tags):
        edge = SplineEdge()
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

    def dxftags(self):
        tags = [
            DXFTag(72, 4),   # edge type
            DXFTag(94, int(self.degree)),
            DXFTag(73, int(self.rational)),
            DXFTag(74, int(self.periodic)),
            DXFTag(95, len(self.knot_values)),  # number of knots
            DXFTag(96, len(self.control_points)),  # number of control points
        ]
        # build knot values list
        # knot values have to be present and valid, otherwise AutoCAD crashes
        if len(self.knot_values):
            tags.extend([DXFTag(40, float(value)) for value in self.knot_values])
        else:
            raise DXFValueError("SplineEdge: missing required knot values")

        # build control points
        # control points have to be present and valid, otherwise AutoCAD crashes
        tags.extend([DXFVertex(10, (float(value[0]), float(value[1]))) for value in self.control_points])

        # build weights list, optional
        tags.extend([DXFTag(42, float(value)) for value in self.weights])

        # build fit points
        # fit points have to be present and valid, otherwise AutoCAD crashes
        # edit 2016-12-20: this is not true - there are cases with no fit points and without crashing AutoCAD
        tags.append(DXFTag(97, len(self.fit_points)))
        tags.extend([DXFVertex(11, (float(value[0]), float(value[1]))) for value in self.fit_points])

        tags.append(DXFVertex(12, (float(self.start_tangent[0]), float(self.start_tangent[1]))))
        tags.append(DXFVertex(13, (float(self.end_tangent[0]), float(self.end_tangent[1]))))
        return tags


EDGE_CLASSES = [None, LineEdge, ArcEdge, EllipseEdge, SplineEdge]


class PatternData(object):
    def __init__(self, hatch):
        self.existing_pattern_start_index = 0
        self.existing_pattern_end_index = 0
        self.lines = self._setup_pattern_lines(hatch.AcDbHatch)

    def _setup_pattern_lines(self, tags):
        try:
            self.existing_pattern_start_index = tags.tag_index(78)  # code 78=Number of patter definition lines
        except DXFValueError:  # no pattern definition lines found
            self.existing_pattern_start_index = 0
            self.existing_pattern_end_index = 0
            return []

        all_pattern_tags = tags.collect_consecutive_tags(PATTERN_DEFINITION_LINE_CODES, start=self.existing_pattern_start_index+1)
        self.existing_pattern_end_index = self.existing_pattern_start_index + len(all_pattern_tags) + 1  # + 1 for Tag(78, Number of boundary paths)
        # existing_pattern_end_index: stored for Hatch._set_pattern_data()
        grouped_line_tags = group_tags(all_pattern_tags, splitcode=53)
        return [PatternDefinitionLine.from_tags(line_tags) for line_tags in grouped_line_tags]

    def clear(self):
        self.lines = []

    def add_line(self, angle=0., base_point=(0., 0.), offset=(0., 0.), dash_length_items=None):
        self.lines.append(self.new_line(angle, base_point, offset, dash_length_items))

    @staticmethod
    def new_line(angle=0., base_point=(0., 0.), offset=(0., 0.), dash_length_items=None):
        if dash_length_items is None:
            raise DXFValueError("Parameter 'dash_length_items' must not be None.")
        return PatternDefinitionLine(angle, base_point, offset, dash_length_items)

    def dxftags(self):
        if len(self.lines):
            tags = [DXFTag(78, len(self.lines))]
            for line in self.lines:
                tags.extend(line.dxftags())
        else:
            tags = []
        return tags

    def __str__(self):
        return "[" + ",".join(str(line) for line in self.lines) + "]"


class PatternDefinitionLine(object):
    def __init__(self,  angle=0., base_point=(0., 0.), offset=(0., 0.), dash_length_items=None):
        self.angle = angle  # as always in degrees (circle = 360 deg)
        self.base_point = base_point
        self.offset = offset
        self.dash_length_items = [] if dash_length_items is None else dash_length_items
        # dash_length_items = [item0, item1, ...]
        # item > 0 is line, < 0 is gap, 0.0 = dot;

    @staticmethod
    def from_tags(tags):
        p = {53: 0, 43: 0, 44: 0, 45: 0, 46: 0}
        dash_length_items = []
        for tag in tags:
            code, value = tag
            if code == 49:
                dash_length_items.append(value)
            else:
                p[code] = value
        return PatternDefinitionLine(p[53], (p[43], p[44]), (p[45], p[46]), dash_length_items)

    def dxftags(self):
        tags = [
            DXFTag(53, self.angle),
            DXFTag(43, self.base_point[0]),
            DXFTag(44, self.base_point[1]),
            DXFTag(45, self.offset[0]),
            DXFTag(46, self.offset[1]),
            DXFTag(79, len(self.dash_length_items)),
        ]
        tags.extend(DXFTag(49, item) for item in self.dash_length_items)
        return tags

    def __str__(self):
        return "[{0.angle}, {0.base_point}, {0.offset}, {0.dash_length_items}]".format(self)


class GradientData(object):
    def __init__(self):
        self.color1 = (0, 0, 0)
        self.color2 = (255, 255, 255)
        self.one_color = 0  # if 1 - a fill that uses a smooth transition between color1 and a specified tint
        self.rotation = 0.  # use grad NOT radians here, because there should be ONE system for all angles
        self.centered = 0.
        self.tint = 0.0
        self.name = 'LINEAR'

    @staticmethod
    def from_tags(tags):
        gdata = GradientData()
        try:
            index = tags.tag_index(450)  # required tag if hatch has gradient data
        except DXFValueError:
            raise DXFStructureError("HATCH: Missing required DXF tag for gradient data (code=450).")
        # if tags[index].value == 0 hatch is a solid ????
        first_color_value = True
        for code, value in tags[index:]:
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

    def dxftags(self):
        return [
            DXFTag(450, 1),  # gradient
            DXFTag(451, 0),  # reserved for the future
            DXFTag(452, self.one_color),  # one (1) or two (0) color gradient
            DXFTag(453, 2),  # number of colors
            DXFTag(460, (self.rotation / 180.) * math.pi),  # rotation angle in radians
            DXFTag(461, self.centered),  # see DXF standard
            DXFTag(462, self.tint),  # see DXF standard
            DXFTag(463, 0),  # first value, see DXF standard
            # code == 63 "color as ACI" can be left off
            DXFTag(421, rgb2int(self.color1)),  # first color
            DXFTag(463, 1),  # second value, see DXF standard
            # code == 63 "color as ACI" can be left off
            DXFTag(421, rgb2int(self.color2)),  # second color
            DXFTag(470, self.name),
        ]

