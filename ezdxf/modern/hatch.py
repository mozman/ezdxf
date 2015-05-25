# Purpose: support for the Ac1015 HATCH entity
# Created: 24.05.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager

from .graphics import none_subclass, entity_subclass
from ..legacy import graphics as legacy
from ..dxfattr import DXFAttr, DXFAttributes, DefSubclass
from ..tags import DXFTag, DXFStructureError, TagGroups
from ..classifiedtags import ClassifiedTags

_HATCH_TPL = """  0
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
52
0.0
41
1.0
77
     0
 47
0.0442352806926743
 98
     1
 10
0.0
 20
0.0
"""

# default is a solid fil hatch
hatch_subclass = DefSubclass('AcDbHatch', {
    'elevation': DXFAttr(10, xtype='Point3D', default=(0.0, 0.0, 0.0)),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
    'pattern_name': DXFAttr(2, default='SOLID'),  # for solid fill
    'solid_fill': DXFAttr(70, default=1),  # pattern fill = 0
    'hatch_style': DXFAttr(75, default=1),  # 0=normal; 1=outer; 2=ignore
    'pattern_type': DXFAttr(76, default=1),  # 0=user; 1=predefined; 2=custom???
    'pattern_angle': DXFAttr(52, default=0.0),  # degrees (360deg = circle)
    'pattern_scale': DXFAttr(41, default=1.0),
    'pattern_double': DXFAttr(77, default=0),  # 0=not double; 1= double
    'n_seed_points': DXFAttr(98),  # number of seed points
})


class Hatch(legacy.GraphicEntity):
    TEMPLATE = ClassifiedTags.from_text(_HATCH_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, hatch_subclass)

    @property
    def AcDbHatch(self):
        return self.tags.subclasses[2]

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

    @contextmanager
    def edit_pattern(self):
        pattern_data = PatternData(self)
        yield pattern_data
        self._set_pattern_data(pattern_data)

    def _set_pattern_data(self, pattern_data):
        pass

    def get_seed_points(self):
        hatch_tags = self.AcDbHatch
        first_seed_point_index = self._get_seed_point_index(hatch_tags)
        seed_points = hatch_tags.collect_consecutive_tags([10], start=first_seed_point_index)
        return [tag.value for tag in seed_points]

    def _get_seed_point_index(self, hatch_tags):
        try:
            seed_count_index = hatch_tags.tag_index(98)  # find index of 'Number of seed points'
        except ValueError:
            raise DXFStructureError("HATCH: Missing required DXF tag 'Number of seed points' (code=98).")
        try:
            first_seed_point_index = hatch_tags.tag_index(10, seed_count_index+1)
        except ValueError:
            raise DXFStructureError("HATCH: Missing required DXF tags 'seed point X value' (code=10).")
        return first_seed_point_index

    def set_seed_points(self, points):
        if len(points) < 1:
            raise ValueError("Param points should be a collection of 2D points and requires at least one point.")
        hatch_tags = self.AcDbHatch
        first_seed_point_index = self._get_seed_point_index(hatch_tags)
        existing_seed_points = hatch_tags.collect_consecutive_tags([10], start=first_seed_point_index)  # don't rely on 'Number of seed points'
        new_seed_points = [DXFTag(10, (point[0], point[1])) for point in points]  # only use x and y coordinate,
        self.dxf.n_seed_points = len(new_seed_points)  # set new count of seed points
        # replace existing seed points
        hatch_tags[first_seed_point_index: first_seed_point_index+len(existing_seed_points)] = new_seed_points

PATH_CODES = frozenset([10, 11, 12, 13, 40, 42, 50, 51, 42, 72, 73, 74, 92, 93, 94, 95, 96, 97, 330])
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
        except ValueError:
            raise DXFStructureError("HATCH: Missing required DXF tag 'Number of boundary paths (loops)' (code=91).")

        self.end_index = self.start_index + 1
        if n_paths == 0:  # created by ezdxf from template without path data
            return paths

        all_path_tags = tags.collect_consecutive_tags(PATH_CODES, start=self.start_index+1)
        self.end_index = self.start_index + len(all_path_tags) + 1  # stored for Hatch._set_boundary_path_data()
        # ... + 1 for Tag(91, Number of boundary paths)
        grouped_path_tags = TagGroups(all_path_tags, splitcode=92)
        for path_tags in grouped_path_tags:
            path_type = path_tags[0]
            is_polyline_path = bool(path_type.value and 2)
            paths.append(PolylinePath(path_tags) if is_polyline_path else EdgePath(path_tags))
        return paths

    def clear(self):
        self.paths = []

    def append_polyline_path(self, path_vertices):
        pass

    def dxftags(self):
        tags = [DXFTag(91, len(self.paths))]
        for path in self.paths:
            tags.extend(path.dxftags())
        return tags

class PolylinePath(object):
    def __init__(self, tags):
        self._path_type = 2
        self.has_bulge = 0
        self.is_closed = 0
        self.vertices = []  # list of 2D coordinates with bulge values (x, y, bulge); bulge default = 0.0
        self.trailing_tags = []
        self._setup_path(tags[1:])

    @property
    def path_type(self):
        return 'PolylinePath'

    def _setup_path(self, tags):
        for tag in tags:
            code, value = tag
            if code == 10:
                self.vertices.append((value[0], value[1], 0.0))  # (x, y, bulge); bulge default = 0.0
            elif code == 42:
                x, y, bulge = self.vertices[-1]
                self.vertices[-1] = (x, y, value)  # replace existing bulge value
            elif code == 92:
                self._path_type = value
            elif code == 72:
                self.has_bulge = value
            elif code == 73:
                self.is_closed = value
            elif code == 93:  # number of polyline vertices
                pass  # ignore this value
            else:  # Ac1027 known tags: 97, 330
                self.trailing_tags.append(tag)

    def dxftags(self):
        vtags = []
        for x, y, bulge in self.vertices:
            vtags.append(DXFTag(10, (float(x), float(y))))
            if bulge != 0:
                vtags.append(DXFTag(42, float(bulge)))
                self.has_bulge = 1

        tags = [DXFTag(92, int(self._path_type)),
                DXFTag(72, int(self.has_bulge)),
                DXFTag(73, int(self.is_closed)),
                DXFTag(93, len(self.vertices)),
                ]
        tags.extend(vtags)
        tags.extend(self.trailing_tags)
        return tags

class EdgePath(object):
    def __init__(self, tags):
        self._path_type = 0

    @property
    def path_type(self):
        return 'EdgePath'

    def dxftags(self):
        return []

class LineEdge(object):
    pass

class ArcEdge(object):
    pass

class EllipseEdge(object):
    pass

class SplineEdge(object):
    pass


class PatternData(object):
    def __init__(self, hatch):
        pass

    def clear(self):
        pass
