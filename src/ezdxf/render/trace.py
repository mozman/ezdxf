# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import List, TYPE_CHECKING, Iterable, Tuple, Dict, Union, cast
from abc import abstractmethod
from collections import namedtuple
from collections.abc import Sequence
import math
from ezdxf.math import Vec2, BSpline, linspace, ConstructionRay, ParallelRaysError, bulge_to_arc, ConstructionArc

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, Drawing, DXFGraphic

__all__ = ['TraceBuilder', 'LinearTrace', 'CurveStation']

LinearStation = namedtuple('LinearStation', ('vertex', 'start_width', 'end_width'))
# start_width of the next (following) segment
# end_width of the next (following) segment

CurveStation = namedtuple('CurveStation', ('vertex0', 'vertex1'))

Face = Tuple[Vec2, Vec2, Vec2, Vec2]
Quadrilateral = Union['Solid', 'Trace', 'Face3d']


class AbstractTrace:
    @abstractmethod
    def faces(self) -> Iterable[Face]:
        pass

    def virtual_entities(self, dxftype='TRACE', dxfattribs: Dict = None, doc: 'Drawing' = None) -> Quadrilateral:
        """
        Yields faces as SOLID, TRACE or 3DFACE entities with DXF attributes given in `dxfattribs`.

        If a document is given, the doc attribute of the new entities will be set and the new
        entities will be automatically added to the entity database of that document.

        Args:
            dxftype: DXF type as string, "SOLID", "TRACE" or "3DFACE"
            dxfattribs: DXF attributes for SOLID, TRACE or 3DFACE entities
            doc: associated document

        """
        from ezdxf.entities.factory import new

        if dxftype not in {'SOLID', 'TRACE', '3DFACE'}:
            raise TypeError(f'Invalid dxftype {dxftype}.')
        dxfattribs = dxfattribs or {}
        for face in self.faces():
            for i in range(4):
                dxfattribs[f'vtx{i}'] = face[i]

            if dxftype != '3DFACE':
                # weird vertex order for SOLID and TRACE
                dxfattribs['vtx2'] = face[3]
                dxfattribs['vtx3'] = face[2]
            entity = new(dxftype, dxfattribs, doc)
            if doc:
                doc.entitydb.add(entity)
            yield entity


class LinearTrace(AbstractTrace):
    """ Linear 2D banded lines like polylines with start- and end width.

    Accepts 3D input, but z-axis is ignored.

    """

    def __init__(self):
        self._stations: List[LinearStation] = []
        self.abs_tol = 1e-12

    def __len__(self):
        return len(self._stations)

    def __getitem__(self, item):
        return self._stations[item]

    @property
    def last_vertex(self):
        """ Returns the last vertex, raises :class:`IndexError` if no station exist. """
        return self._stations[-1].vertex

    @property
    def last_station(self):
        """ Returns the last station, raises :class:`IndexError` if no station exist. """
        return self._stations[-1]

    @property
    def is_started(self) -> bool:
        """ `True` if at least one station exist. """
        return bool(self._stations)

    def add_station(self, point: 'Vertex', start_width: float, end_width: float = None) -> None:
        """
        Add a trace station (like a vertex) at location `point`, `start_width` is the width of the next
        segment starting at this station, `end_width` is the end width of the next segment.

        Adding the last location again, replaces the actual last location e.g. adding lines (a, b), (b, c),
        creates only 3 stations (a, b, c), this is very important to connect to/from splines.

        Args:
            point: 2D location (vertex), z-axis of 3D vertices is ignored.
            start_width: start width of next segment
            end_width:  end width of next segment

        """
        if end_width is None:
            end_width = start_width
        point = Vec2(point)
        if self.is_started and self.last_vertex.isclose(point, self.abs_tol):
            # replace last station
            self._stations.pop()
        self._stations.append(LinearStation(point, float(start_width), float(end_width)))

    def faces(self) -> Iterable[Face]:
        """ Yields all faces as 4-tuples of :class:`~ezdxf.math.Vec2` objects.

        First and last miter is 90 degrees if the path is not closed, otherwise the
        intersection of first and last segment is taken into account,
        a closed path has to have explicit the same last and first vertex.

        """
        count = len(self._stations)
        if count < 2:
            raise ValueError('Two or more stations required.')

        def offset_rays(segment):
            up1, up2, low1, low2 = segments[segment]
            if up1.isclose(up2):
                angle = (self._stations[segment].vertex - self._stations[segment + 1].vertex).angle
                offset_ray1 = ConstructionRay(up1, angle)
            else:
                offset_ray1 = ConstructionRay(up1, up2)

            if low1.isclose(low2):
                angle = (self._stations[segment].vertex - self._stations[segment + 1].vertex).angle
                offset_ray2 = ConstructionRay(low1, angle)
            else:
                offset_ray2 = ConstructionRay(low1, low2)
            return offset_ray1, offset_ray2

        # todo: closed paths
        is_closed = self._stations[0].vertex.isclose(self.last_vertex)

        segments = []
        for station in range(count - 1):
            start, sw1, ew1 = self._stations[station]
            end, sw2, ew2 = self._stations[station + 1]
            segments.append(_normal_offset_points(start, end, sw1, ew1))

        offset_ray1, offset_ray2 = offset_rays(0)
        prev_offset_ray1 = offset_ray1
        prev_offset_ray2 = offset_ray2
        for i in range(len(segments)):
            up1, up2, low1, low2 = segments[i]
            if i == 0:
                vtx0 = up1
                vtx1 = low1
                prev_offset_ray1 = offset_ray1
                prev_offset_ray2 = offset_ray2
            else:
                try:
                    vtx0 = prev_offset_ray1.intersect(offset_ray1)
                except ParallelRaysError:
                    vtx0 = up1
                try:
                    vtx1 = prev_offset_ray2.intersect(offset_ray2)
                except ParallelRaysError:
                    vtx1 = low1

            if i < len(segments) - 1:
                next_offset_ray1, next_offset_ray2 = offset_rays(i + 1)
                try:
                    vtx2 = offset_ray2.intersect(next_offset_ray2)
                except ParallelRaysError:
                    vtx2 = low2
                try:
                    vtx3 = offset_ray1.intersect(next_offset_ray1)
                except ParallelRaysError:
                    vtx3 = up2

                prev_offset_ray1 = offset_ray1
                prev_offset_ray2 = offset_ray2
                offset_ray1 = next_offset_ray1
                offset_ray2 = next_offset_ray2
            else:
                vtx2 = low2
                vtx3 = up2
            yield vtx0, vtx1, vtx2, vtx3


def _normal_offset_points(start: Vec2, end: Vec2, start_width: float, end_width: float) -> Face:
    dir_vector = (end - start).normalize()
    ortho = dir_vector.orthogonal(True)
    offset_start = ortho.normalize(start_width / 2)
    offset_end = ortho.normalize(end_width / 2)
    return start + offset_start, end + offset_end, start - offset_start, end - offset_end


class CurvedTrace(AbstractTrace):
    """ 2D banded curves like arcs or splines with start- and end width.

    Represents one curved entity.

    Accepts 3D input, but z-axis is ignored.

    """

    def __init__(self):
        self._stations: List[CurveStation] = []

    def __len__(self):
        return len(self._stations)

    def __getitem__(self, item):
        return self._stations[item]

    @classmethod
    def from_spline(cls, spline: BSpline, start_width: float, end_width: float, segments: int) -> 'CurvedTrace':
        curve_trace = cls()
        count = segments + 1
        t = linspace(0, spline.max_t, count)
        for ((point, derivative), width) in zip(spline.derivatives(t, n=1), linspace(start_width, end_width, count)):
            normal = Vec2(derivative).orthogonal(True)
            curve_trace.append(Vec2(point), normal, width)
        return curve_trace

    @classmethod
    def from_arc(cls, arc: ConstructionArc, start_width: float, end_width: float, segments: int) -> 'CurvedTrace':
        curve_trace = cls()
        count = segments + 1
        center = Vec2(arc.center)
        for point, width in zip(arc.vertices(arc.angles(count)), linspace(start_width, end_width, count)):
            curve_trace.append(point, point - center, width)
        return curve_trace

    def append(self, point: Vec2, normal: Vec2, width: float) -> None:
        """
        Add a curve trace station (like a vertex) at location `point`^.

        Args:
            point: 2D curve location (vertex), z-axis of 3D vertices is ignored.
            normal: curve normal
            width:  width of station

        """
        normal = normal.normalize(width / 2)
        self._stations.append(CurveStation(point + normal, point - normal))

    def faces(self) -> Iterable[Face]:
        """ Yields all faces as 4-tuples of :class:`~ezdxf.math.Vec2` objects.
        """
        count = len(self._stations)
        if count < 2:
            raise ValueError('Two or more stations required.')

        vtx0 = None
        vtx1 = None
        for vtx2, vtx3 in self._stations:
            if vtx0 is None:
                vtx0 = vtx3
                vtx1 = vtx2
                continue
            yield vtx0, vtx1, vtx2, vtx3
            vtx0 = vtx3
            vtx1 = vtx2


class TraceBuilder(Sequence):
    """ Sequence of 2D banded lines like polylines with start- and end width or curves with start- and end width.

    Accepts 3D input, but z-axis is ignored.

    """

    def __init__(self, default_start_width=None):
        self._traces: List[AbstractTrace] = []
        self.abs_tol = 1e-12

    def __len__(self):
        return len(self._traces)

    def __getitem__(self, item):
        return self._traces[item]

    def append(self, trace: AbstractTrace) -> None:
        self._traces.append(trace)

    def faces(self) -> Iterable[Face]:
        """ Yields all faces as 4-tuples of :class:`~ezdxf.math.Vec2` objects.
        """
        for trace in self._traces:
            yield from trace.faces()

    def virtual_entities(self, dxftype='TRACE', dxfattribs: Dict = None, doc: 'Drawing' = None) -> Quadrilateral:
        """
        Yields faces as SOLID, TRACE or 3DFACE entities with DXF attributes given in `dxfattribs`.

        If a document is given, the doc attribute of the new entities will be set and the new
        entities will be automatically added to the entity database of that document.

        Args:
            dxftype: DXF type as string, "SOLID", "TRACE" or "3DFACE"
            dxfattribs: DXF attributes for SOLID, TRACE or 3DFACE entities
            doc: associated document

        """
        for trace in self._traces:
            yield from trace.virtual_entities(dxftype, dxfattribs, doc)

    @classmethod
    def from_polyline(cls, polyline: 'DXFGraphic', segments: int = 40) -> 'TraceBuilder':
        dxftype = polyline.dxftype()
        if dxftype == 'LWPOLYLINE':
            polyline = cast('LWPOLYLINE', polyline)
            const_width = polyline.dxf.const_width
            points = []
            for x, y, start_width, end_width, bulge in polyline.lwpoints:
                location = Vec2(x, y)
                if const_width:
                    start_width = const_width
                    end_width = const_width
                points.append((location, start_width, end_width, bulge))
            closed = polyline.closed
        elif dxftype == 'POLYLINE':
            polyline = cast('POLYLINE', polyline)
            if not polyline.is_2d_polyline:
                raise TypeError('2D POLYLINE required')
            closed = polyline.is_closed
            default_start_width = polyline.dxf.default_start_width
            default_end_width = polyline.dxf.default_end_width
            points = []
            for vertex in polyline.vertices:
                location = Vec2(vertex.dxf.location)
                if vertex.dxf.has_attr('start_width'):
                    start_width = vertex.dxf.start_width
                else:
                    start_width = default_start_width
                if vertex.dxf.has_attr('end_width'):
                    end_width = vertex.dxf.end_width
                else:
                    end_width = default_end_width
                bulge = vertex.dxf.bulge
                points.append((location, start_width, end_width, bulge))
        else:
            raise TypeError(f'Invalid DXF type {dxftype}')

        trace = cls()
        store_bulge = None
        store_start_width = None
        store_end_width = None
        store_point = None

        # todo: closed polygons
        linear_trace = LinearTrace()
        for point, start_width, end_width, bulge in points:
            if store_bulge:
                center, start_angle, end_angle, radius = bulge_to_arc(store_point, point, store_bulge)
                arc = ConstructionArc(
                    center,
                    radius,
                    math.degrees(start_angle),
                    math.degrees(end_angle),
                    is_counter_clockwise=True,
                )
                if arc.start_point.isclose(point):
                    sw = store_end_width
                    ew = store_start_width
                else:
                    ew = store_end_width
                    sw = store_start_width

                trace.append(CurvedTrace.from_arc(arc, sw, ew, segments))
                store_bulge = None

            if bulge != 0:  # arc from prev_point to point
                if linear_trace.is_started:
                    linear_trace.add_station(point, start_width, end_width)
                    trace.append(linear_trace)
                    linear_trace = LinearTrace()
                store_bulge = bulge
                store_start_width = start_width
                store_end_width = end_width
                store_point = point
                continue

            linear_trace.add_station(point, start_width, end_width)
        if linear_trace.is_started:
            trace.append(linear_trace)
        return trace
