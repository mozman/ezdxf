# Purpose: support for the AcDb1015 HATCH entity
# Created: 24.05.2015
# Copyright (C) 2015, Manfred Moitzi
# License: MIT License

from __future__ import unicode_literals
__author__ = "mozman <mozman@gmx.at>"

from contextlib import contextmanager

from .graphics import none_subclass, entity_subclass
from ..legacy import graphics as legacy
from ..dxfattr import DXFAttr, DXFAttributes, DefSubclass
from ..tags import DXFTag, DXFStructureError
from ..classifiedtags import ClassifiedTags
from .. import const

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
        pass

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
        seed_points = hatch_tags.collect([10], start=first_seed_point_index)
        return [tag.value for tag in seed_points]

    def _get_seed_point_index(self, hatch_tags):
        try:
            seed_count_index = hatch_tags.tag_index(98)  # find index of 'Number of seed points'
        except ValueError:
            raise DXFStructureError("Missing required DXF tag 'Number of seed points' (code=98).")
        try:
            first_seed_point_index = hatch_tags.tag_index(10, seed_count_index+1)
        except ValueError:
            raise DXFStructureError("Missing required DXF tags 'seed point X value' (code=10).")
        return first_seed_point_index

    def set_seed_points(self, points):
        if len(points) < 1:
            raise ValueError("Param points should be a collection of 2D points and requires at least one point.")
        hatch_tags = self.AcDbHatch
        first_seed_point_index = self._get_seed_point_index(hatch_tags)
        existing_seed_points = hatch_tags.collect([10], start=first_seed_point_index)  # don't rely on 'Number of seed points'
        new_seed_points = [DXFTag(10, (point[0], point[1])) for point in points]  # only use x and y coordinate,
        self.dxf.n_seed_points = len(new_seed_points)  # set new count of seed points
        # replace existing seed points
        hatch_tags[first_seed_point_index: first_seed_point_index+len(existing_seed_points)] = new_seed_points


class BoundaryPathData(object):
    def __init__(self, hatch):
        pass

    def clear(self):
        pass


class PatternData(object):
    def __init__(self, hatch):
        pass

    def clear(self):
        pass
