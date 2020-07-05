# Copyright (c) 2020, Manfred Moitzi
# License: MIT License
from typing import List, TYPE_CHECKING
from collections import namedtuple
from collections.abc import Sequence
from ezdxf.math import Vec2, BSpline, linspace

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

__all__ = ['TraceBuilder']

Station = namedtuple('Station', ('vertex', 'start_width', 'end_width'))


# start_width of the next (following) segment
# end_width of the next (following) segment


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
    def last_point(self):
        return self._stations[-1].vertex

    @property
    def last_station(self):
        return self._stations[-1]

    @property
    def is_started(self):
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
        if self.is_started and self.last_point.isclose(point, self.abs_tol):  # replace last station
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
        :attr:`TraceBuilder.end_vertex`. It is not a problem if this is not the case, the last station
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
