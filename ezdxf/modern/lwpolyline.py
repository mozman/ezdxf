# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from contextlib import contextmanager
import array
from ..lldxf.types import DXFTag, DXFVertex
from ..lldxf.packedtags import VertexArray, replace_tags
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..lldxf import loader

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


class LWPolylinePoints(VertexArray):
    code = -10  # compatible with DXFTag.code
    VERTEX_CODE = 10
    START_WIDTH_CODE = 40
    END_WIDTH_CODE = 41
    BULGE_CODE = 42
    VERTEX_SIZE = 5
    __slots__ = ('value', )

    @classmethod
    def from_tags(cls, tags):
        """
        Setup point array from extended tags.

        Args:
            tags: ExtendedTags() object

        """
        subclass = tags.get_subclass('AcDbPolyline')

        def get_vertex():
            point.append(attribs.get(cls.START_WIDTH_CODE, 0))
            point.append(attribs.get(cls.END_WIDTH_CODE, 0))
            point.append(attribs.get(cls.BULGE_CODE, 0))
            return tuple(point)
        data = []
        point = None
        attribs = {}
        for tag in subclass:
            if tag.code in LWPOINTCODES:
                if tag.code == 10:
                    if point is not None:
                        data.extend(get_vertex())
                    point = list(tag.value[0:2])  # just use x, y coordinates, z is invalid but you never know!
                    attribs = {}
                else:
                    attribs[tag.code] = tag.value
        if point is not None:
            data.extend(get_vertex())
        return cls(data=data)

    def append(self, point):
        super(LWPolylinePoints, self).append(point_to_array(point))

    def dxftags(self):
        for point in self:
            x, y, start_width, end_width, bulge = point
            yield DXFVertex(self.VERTEX_CODE, (x, y))
            if start_width:
                yield DXFTag(self.START_WIDTH_CODE, start_width)
            if end_width:
                yield DXFTag(self.END_WIDTH_CODE, end_width)
            if bulge:
                yield DXFTag(self.BULGE_CODE, bulge)


def point_to_array(point):
    double_point = array.array('d', point)
    if len(double_point) < 5:
        double_point.extend((0., )*(5-len(double_point)))
    return double_point


@loader.register('LWPOLYLINE', legacy=False)
def tag_processor(tags):
    points = LWPolylinePoints.from_tags(tags)
    subclass = tags.get_subclass('AcDbPolyline')
    replace_tags(subclass, codes=LWPOINTCODES, packed_data=points)
    return tags


class LWPolyline(ModernGraphicEntity):
    TEMPLATE = tag_processor(ExtendedTags.from_text(_LWPOLYLINE_TPL))
    DXFATTRIBS = DXFAttributes(none_subclass, entity_subclass, lwpolyline_subclass)
    CLOSED = 1
    PLINEGEN = 128

    @property
    def AcDbPolyline(self):
        return self.tags.subclasses[2]

    @property
    def closed(self):
        return self.get_flag_state(self.CLOSED, name='flags')

    @property
    def packed_points(self):
        return self.AcDbPolyline.get_first_tag(LWPolylinePoints.code)

    @closed.setter
    def closed(self, status):
        self.set_flag_state(self.CLOSED, status, name='flags')

    def __len__(self):
        return len(self.packed_points)

    def __iter__(self):
        """
        Yielding tuples of (x, y, start_width, end_width, bulge), start_width, end_width and bulge is 0 if not present.

        """
        return iter(self.packed_points)

    get_points = __iter__

    def __getitem__(self, index):
        """
        Returns polyline point at *index* as (x, y, start_width, end_width, bulge) tuple, start_width, end_width and
        bulge is 0 if not present.

        """
        return self.packed_points[index]

    def __setitem__(self, index, value):
        """
        Set polyline point at position index.

        Args:
            index: point index
            value: point value as (x, y, [start_width, [end_width, [bulge]]]) tuple

        """
        self.packed_points[index] = point_to_array(value)

    def __delitem__(self, index):
        del self.packed_points[index]
        self.update_count()

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
        for x, y in self.vertices():
            yield ocs.to_wcs((x, y, elevation))

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
        self.packed_points.extend(points)
        self.update_count()

    def update_count(self):
        self.dxf.count = len(self.packed_points)

    def set_points(self, points):
        """
        Remove all points and append new *points*, *points* is a list of (x, y, [start_width, [end_width, [bulge]]])
        tuples. Set start_width, end_width to 0 to ignore (x, y, 0, 0, bulge).

        """
        self.discard_points()
        self.append_points(points)

    @contextmanager
    def points(self):
        points = self.packed_points
        yield points
        self.update_count()

    @contextmanager
    def rstrip_points(self):
        points = list(self.get_rstrip_points())
        yield points
        self.set_points(points)

    def discard_points(self):
        self.packed_points.clear()
        self.dxf.count = 0
