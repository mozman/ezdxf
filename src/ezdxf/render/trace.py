# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import List, TYPE_CHECKING, Iterable, Tuple, Dict, Union
from collections import namedtuple
from collections.abc import Sequence
from ezdxf.math import Vec2, BSpline, linspace, ConstructionRay, ParallelRaysError

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, Solid, Trace, Face3d, Drawing

__all__ = ['TraceBuilder']

Station = namedtuple('Station', ('vertex', 'start_width', 'end_width'))

# start_width of the next (following) segment
# end_width of the next (following) segment
Face = Tuple[Vec2, Vec2, Vec2, Vec2]


class TraceBuilder(Sequence):
    """ Build 2D banded lines like polylines with start- and end width.

    Accepts 3D input, but z-axis is ignored.

    """

    def __init__(self, default_start_width=None):
        self._stations: List[Station] = []
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
        self._stations.append(Station(point, float(start_width), float(end_width)))

    def add_spline(self, spline: BSpline, start_width: float, end_width: float, segments: int) -> None:
        """
        Add a B-spline by approximation of `segments`, start- and end-width of segments is linear interpolated from
        `start_width` to `end_width`.

        Use :class:`~ezdxf.math.BSpline` constructors :meth:`~ezdxf.math.BSpline.from_arc` and
        :meth:`~ezdxf.math.BSpline.from_ellipse` to add arcs and ellipses, but check for continuity and reverse
        splines if necessary, because the DXF format stores ARC and ELLIPSE entities always in counter clockwise
        direction, it is not possible to represent clockwise arcs or ellipses.

        Continuity means the first control point of a clamped spline should be close to the actual
        :attr:`TraceBuilder.last_vertex`. It is not a problem if this is not the case, the last station
        will be connected to the first spline vertex, but this is often not the expected result.

        Args:
            spline: :class:`~ezdxf.math.BSpline` object
            start_width: overall start width
            end_width: overall end width
            segments: count of approximation segments

        """
        start_width = float(start_width)
        end_width = float(end_width)
        widths = list(linspace(start_width, end_width, segments + 1))
        widths.append(widths[-1])  # end width of last segment
        for index, vertex in enumerate(spline.approximate(int(segments))):
            self.add_station(vertex, widths[index], widths[index + 1])

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

    def virtual_entities(self, dxftype='TRACE', dxfattribs: Dict = None, doc: 'Drawing' = None) -> Union[
        'Solid', 'Trace', 'Face3d']:
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


def _normal_offset_points(start: Vec2, end: Vec2, start_width: float, end_width: float) -> Face:
    dir_vector = (end - start).normalize()
    ortho = dir_vector.orthogonal(True)
    offset_start = ortho.normalize(start_width / 2)
    offset_end = ortho.normalize(end_width / 2)
    return start + offset_start, end + offset_end, start - offset_start, end - offset_end
