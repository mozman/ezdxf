# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from contextlib import contextmanager
import array
from ..lldxf.types import DXFTag
from ..lldxf.const import DXFIndexError, DXFValueError
from ..lldxf.packedtags import PackedTags
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
PACKED_POINTS_CODE = -10  # good idea? or better just 10


class PackedPoints(PackedTags):
    __slots__ = ('code', 'value')

    def __init__(self):
        self.code = PACKED_POINTS_CODE  # compatible with DXFTag.code
        self.value = array.array('d')  # compatible with DXFTag.value

    def __len__(self):
        return len(self.value) // 5

    def __getitem__(self, index):
        return self.get_point(index)

    def __setitem__(self, index, point):
        self.set_point(index, point)

    def clone(self):
        p = PackedPoints()
        p.code = self.code
        p.value = array.array('d', self.value)
        return p

    def setup(self, tags):
        """
        Setup point array from extended tags.

        Args:
            tags: ExtendedTags() object

        """
        subclass = tags.get_subclass('AcDbPolyline')

        def get_vertex():
            point.append(attribs.get(40, 0))
            point.append(attribs.get(41, 0))
            point.append(attribs.get(42, 0))
            return tuple(point)

        point = None
        attribs = {}
        for tag in subclass:
            if tag.code in LWPOINTCODES:
                if tag.code == 10:
                    if point is not None:
                        self.append(get_vertex())
                    point = list(tag.value[0:2])  # just use x, y coordinates, z is invalid but you never know!
                    attribs = {}
                else:
                    attribs[tag.code] = tag.value
        if point is not None:
            self.append(get_vertex())

    def real_index(self, index):
        if index >= len(self):
            raise IndexError
        elif index < 0:
            index += len(self)
            if index < 0:
                raise IndexError
        return index

    def get_point(self, index):
        index = self.real_index(index) * 5
        return tuple(self.value[index:index+5])

    def set_point(self, index, point):
        if len(point) != 5:
            raise DXFValueError('point requires exact 5 components.')
        if isinstance(point, (tuple, list)):
            point = array.array('d', point)
        index = self.real_index(index) * 5
        self.value[index:index+5] = point

    def dxftags(self):
        for point in self:
            x, y, start_width, end_width, bulge = point
            yield DXFTag(10, (x, y))
            if start_width:
                yield DXFTag(40, start_width)
            if end_width:
                yield DXFTag(41, end_width)
            if bulge:
                yield DXFTag(42, bulge)

    def append(self, point):
        # PackedPoints does not maintain the point count attribute!
        if len(point) != 5:
            raise DXFValueError('point requires exact 5 components.')
        self.value.extend(point)

    def clear(self):
        del self.value[:]


def point_to_array(point):
    double_point = array.array('d', point)
    if len(double_point) < 5:
        double_point.extend((0., )*(5-len(double_point)))
    return double_point


def replace_point_tags(tags, packed_points):
    """
    Replace single DXF tags for points, start_width, end_width and bulge by PackedPoints() object.

    Args:
        tags: ExtendedTags
        packed_points: PackedPoints() object

    """
    subclass = tags.get_subclass('AcDbPolyline')
    try:
        pos = subclass.tag_index(10)
    except ValueError:
        pos = len(subclass)
    subclass.remove_tags(codes=LWPOINTCODES)
    subclass.insert(pos, packed_points)


@loader.register('LWPOLYLINE', legacy=False)
def tag_processor(tags):
    points = PackedPoints()
    points.setup(tags)
    replace_point_tags(tags, points)
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
        return self.AcDbPolyline.get_first_tag(PACKED_POINTS_CODE)

    @closed.setter
    def closed(self, status):
        self.set_flag_state(self.CLOSED, status, name='flags')

    def __len__(self):
        return self.dxf.count

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
        try:
            return self.packed_points.get_point(index)
        except IndexError:
            raise DXFIndexError

    def __setitem__(self, index, value):
        """
        Set polyline point at position index.

        Args:
            index: point index
            value: point value as (x, y, [start_width, [end_width, [bulge]]]) tuple

        """
        try:
            self.packed_points.set_point(index, point_to_array(value))
        except IndexError:
            raise DXFIndexError

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
        packed_points = self.packed_points
        for point in points:
            packed_points.append(point_to_array(point))

        self._update_count()

    def _update_count(self):
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
        points = list(self)
        yield points
        self.set_points(points)

    @contextmanager
    def rstrip_points(self):
        points = list(self.get_rstrip_points())
        yield points
        self.set_points(points)

    def discard_points(self):
        self.packed_points.clear()
        self.dxf.count = 0
