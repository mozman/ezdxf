# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from contextlib import contextmanager
from ..lldxf.types import DXFTag
from ..lldxf.const import DXFIndexError
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity


_LWPOLYLINE_TPL = """0
LWPOLYLINE
5
0
330
0
100
AcDbEntity
8
0
100
AcDbPolyline
90
0
70
0
"""

lwpolyline_subclass = DefSubclass('AcDbPolyline', {
    'elevation': DXFAttr(38, default=0.0),
    'thickness': DXFAttr(39, default=0.0),
    'flags': DXFAttr(70, default=0),
    'const_width': DXFAttr(43, default=0.0),
    'count': DXFAttr(90),
    'extrusion': DXFAttr(210, xtype='Point3D', default=(0.0, 0.0, 1.0)),
})

LWPOINTCODES = (10, 20, 40, 41, 42)


class LWPolyline(ModernGraphicEntity):
    TEMPLATE = ExtendedTags.from_text(_LWPOLYLINE_TPL)
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, lwpolyline_subclass)
    CLOSED = 1
    PLINEGEN = 128

    @property
    def AcDbPolyline(self):
        return self.tags.subclasses[2]

    @property
    def closed(self):
        return self.get_flag_state(self.CLOSED, name='flags')

    @closed.setter
    def closed(self, status):
        self.set_flag_state(self.CLOSED, status, name='flags')

    def __len__(self):
        return self.dxf.count

    def __iter__(self):
        """
        Yielding tuples of (x, y, start_width, end_width, bulge), start_width, end_width and bulge is 0 if not present.

        """
        def get_vertex():
            point.append(attribs.get(40, 0))
            point.append(attribs.get(41, 0))
            point.append(attribs.get(42, 0))
            return tuple(point)

        point = None
        attribs = {}
        for tag in self.AcDbPolyline:
            if tag.code in LWPOINTCODES:
                if tag.code == 10:
                    if point is not None:
                        yield get_vertex()
                    point = list(tag.value[0:2])  # just use x, y coordinates, z is invalid but you never know!
                    attribs = {}
                else:
                    attribs[tag.code] = tag.value
        if point is not None:
            yield get_vertex()  # last point

    def vertices(self):
        """
        Yields all points as (x, y) tuples.

        """
        for point in self:
            yield point[0], point[1]

    def vertices_in_wcs(self):
        """
        Yields all points as (x, y, z) tuples in WCS.

        """
        ocs = self.ocs()
        elevation = self.get_dxf_attrib('elevation', default=0.)
        for vertex in self.vertices():
            yield ocs.to_wcs((vertex[0], vertex[1], elevation))

    def get_rstrip_points(self):
        last0 = 4
        for point in self:
            while point[last0] == 0 and last0 > 1:
                last0 -= 1
            yield tuple(point[:last0+1])

    def append_points(self, points):
        """
        Append new *points* to polyline, *points* is a list of (x, y, [start_width, [end_width, [bulge]]])
        tuples. Set start_width, end_width to 0 to ignore (x, y, 0, 0, bulge).

        """
        tags = self.AcDbPolyline

        def append_point(point):

            def add_tag_if_not_zero(code, value):
                if value != 0.0:
                    tags.append(DXFTag(code, value))
            tags.append(DXFTag(10, (point[0], point[1])))  # x, y values
            try:
                add_tag_if_not_zero(40, point[2])  # start width, default=0
                add_tag_if_not_zero(41, point[3])  # end width, default=0
                add_tag_if_not_zero(42, point[4])  # bulge, default=0
            except IndexError:  # internal exception
                pass

        for point in points:
            append_point(point)

        self._update_count()

    def _update_count(self):
        self.dxf.count = len(self.AcDbPolyline.find_all(10))

    get_points = __iter__

    def set_points(self, points):
        """ Remove all points and append new *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]])
        tuples. Set start_width, end_width to 0 to ignore (x, y, 0, 0, bulge).
        """
        self.discard_points()
        self.append_points(points)

    @contextmanager
    def points(self):
        points = list(self)
        yield points
        self.set_points(points)

    @contextmanager
    def rstrip_points(self):
        points = list(self.get_rstrip_points())
        yield points
        self.set_points(points)

    def discard_points(self):
        self.AcDbPolyline.remove_tags(codes=LWPOINTCODES)
        self.dxf.count = 0

    def __getitem__(self, index):
        """ Returns polyline point at *index* as (x, y, start_width, end_width, bulge) tuple, start_width, end_width and
        bulge is 0 if not present.
        """
        if index < 0:
            index += self.dxf.count
        for x, point in enumerate(self):
            if x == index:
                return point
        raise DXFIndexError(index)
