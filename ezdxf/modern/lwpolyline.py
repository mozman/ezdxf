# Created: 25.03.2011
# Copyright (c) 2011-2018, Manfred Moitzi
# License: MIT License
from __future__ import unicode_literals
from contextlib import contextmanager
import array
from ..lldxf.types import DXFTag, DXFVertex
from ..lldxf.attributes import DXFCallback
from ..lldxf.packedtags import VertexArray, replace_tags
from .graphics import ExtendedTags, DXFAttr, DefSubclass, DXFAttributes
from .graphics import none_subclass, entity_subclass, ModernGraphicEntity
from ..lldxf import loader

FORMAT_CODES = frozenset('xysebv')
DEFAULT_FORMAT = 'xyseb'

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
    'count': DXFCallback(getter='__len__'),  # LWPolyline.__len__()
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

    def append(self, point, format=DEFAULT_FORMAT):
        super(LWPolylinePoints, self).append(compile_array(point, format=format))

    def dxftags(self):
        yield DXFTag(90, len(self))
        for point in self:
            x, y, start_width, end_width, bulge = point
            yield DXFVertex(self.VERTEX_CODE, (x, y))
            if start_width:
                yield DXFTag(self.START_WIDTH_CODE, start_width)
            if end_width:
                yield DXFTag(self.END_WIDTH_CODE, end_width)
            if bulge:
                yield DXFTag(self.BULGE_CODE, bulge)


REMOVE_CODES = LWPOINTCODES + (90, )


@loader.register('LWPOLYLINE', legacy=False)
def tag_processor(tags):
    points = LWPolylinePoints.from_tags(tags)
    subclass = tags.get_subclass('AcDbPolyline')
    replace_tags(subclass, codes=REMOVE_CODES, packed_data=points)
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
    def lwpoints(self):
        return self.AcDbPolyline.get_first_tag(LWPolylinePoints.code)

    @closed.setter
    def closed(self, status):
        self.set_flag_state(self.CLOSED, status, name='flags')

    def __len__(self):
        return len(self.lwpoints)

    def __iter__(self):
        """
        Yielding tuples of (x, y, start_width, end_width, bulge).

        """
        return iter(self.lwpoints)

    def __getitem__(self, index):
        """
        Returns polyline point at position index as (x, y, start_width, end_width, bulge) tuple.

        """
        return self.lwpoints[index]

    def __setitem__(self, index, value):
        """
        Set polyline point at position index. Point format is fixed as 'xyseb'.

        Args:
            index: point index
            value: point value as (x, y, [start_width, [end_width, [bulge]]]) tuple

        """
        self.lwpoints[index] = compile_array(value)

    def __delitem__(self, index):
        del self.lwpoints[index]

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

    def append(self, point, format=DEFAULT_FORMAT):
        """
        Append point to polyline, format specifies a user defined point format.

        Args:
            point: (x, y, [start_width, [end_width, [bulge]]]) tuple
            format: format string, default is 'xyseb'
                x = x coordinate
                y = y coordinate
                s = start width
                e = end width
                b = bulge value
                v = (x, y) as tuple

        """
        self.lwpoints.append(point, format=format)

    def insert(self, pos, point, format=DEFAULT_FORMAT):
        """
        Insert new point in front of positions pos, format specifies a user defined point format.

        Args:
            pos: insert position
            point: point data
            format: format string, default is 'xyseb'
                x = x coordinate
                y = y coordinate
                s = start width
                e = end width
                b = bulge value
                v = (x, y) as tuple

        """
        data = compile_array(point, format=format)
        self.lwpoints.insert(pos, data)

    def append_points(self, points, format=DEFAULT_FORMAT):
        """
        Append new points to polyline, format specifies a user defined point format.

        Args:
            points: iterable of point, point is (x, y, [start_width, [end_width, [bulge]]]) tuple
            format: format string, default is 'xyseb'
                x = x coordinate
                y = y coordinate
                s = start width
                e = end width
                b = bulge value
                v = (x, y) as tuple

        """
        for point in points:
            self.lwpoints.append(point, format=format)

    @contextmanager
    def points(self, format=DEFAULT_FORMAT):
        points = self.get_points(format=format)
        yield points
        self.set_points(points, format=format)

    def get_points(self, format=DEFAULT_FORMAT):
        """
        Returns all points as list of tuples, format specifies a user defined point format.

        Args:
            format: format string, default is 'xyseb'
                x = x coordinate
                y = y coordinate
                s = start width
                e = end width
                b = bulge value
                v = (x, y) as tuple

        """
        return [format_point(p, format=format) for p in self.lwpoints]

    def set_points(self, points, format=DEFAULT_FORMAT):
        """
        Remove all points and append new points.

        Args:
            points: iterable of point, point is (x, y, [start_width, [end_width, [bulge]]]) tuple
            format: format string, default is 'xyseb'
                x = x coordinate
                y = y coordinate
                s = start width
                e = end width
                b = bulge value
                v = (x, y) as tuple

        """
        self.lwpoints.clear()
        self.append_points(points, format=format)

    def clear(self):
        self.lwpoints.clear()


def format_point(point, format='xyseb'):
    """
    Reformat point components.

    Args:
        point: list or tuple of (x, y, start_width, end_width, bulge)
        format: format string, default is 'xyseb'
            x = x coordinate
            y = y coordinate
            s = start width
            e = end width
            b = bulge value
            v = (x, y) as tuple

    Returns: tuple of selected components

    """
    x, y, s, e, b = point
    v = (x, y)
    vars = locals()
    return tuple(vars[code] for code in format.lower() if code in FORMAT_CODES)


def compile_array(data, format='xyseb'):
    """
    Gather point components from input data.

    Args:
        data: list or tuple of point components
        format: format string, default is 'xyseb'
            x = x coordinate
            y = y coordinate
            s = start width
            e = end width
            b = bulge value
            v = (x, y) as tuple

    Returns: array.array('d', (x, y, start_width, end_width, bulge))

    """
    a = array.array('d', (0., 0., 0., 0., 0.))
    format = [code for code in format.lower() if code in FORMAT_CODES]
    for code, value in zip(format, data):
        if code not in FORMAT_CODES:
            continue
        if code == 'v':
            a[0] = value[0]
            a[1] = value[1]
        else:
            a['xyseb'.index(code)] = value
    return a


