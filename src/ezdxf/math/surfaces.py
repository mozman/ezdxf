# Copyright (c) 2012-2021, Manfred Moitzi
# License: MIT License
from typing import List, TYPE_CHECKING
from .bezier import bernstein_basis
from ezdxf.math import Vec3, NULLVEC

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex

__all__ = ["BezierSurface"]


class BezierSurface:
    """:class:`BezierSurface` defines a mesh of `m` x `n` control points.
    This is a parametric surface, which means the `m`-dimension goes from ``0``
    to ``1`` as parameter `u` and the `n`-dimension goes from ``0`` to ``1`` as
    parameter `v`.

    Args:
        defpoints: matrix (list of lists) of `m` rows and `n` columns:
                   [ [m1n1, m1n2, ... ], [m2n1, m2n2, ...] ... ]  each element is a
                   3D location as ``(x, y, z)`` tuple.

    """

    def __init__(self, defpoints: List[List["Vertex"]]):
        self._defpoints = defpoints

    @property
    def nrows(self):
        """count of rows (m-dimension)"""
        return len(self._defpoints)

    @property
    def ncols(self):
        """count of columns (n-dimension)"""
        return len(self._defpoints[0])

    def approximate(self, usegs: int, vsegs: int) -> List[List[Vec3]]:
        """Approximate surface as grid of ``(x, y, z)`` :class:`Vec3`.

        Args:
            usegs: count of segments in `u`-direction (m-dimension)
            vsegs: count of segments in `v`-direction (n-dimension)

        Returns:
            list of `usegs` + 1 rows, each row is a list of `vsegs` + 1 vertices
            as :class:`Vec3`.

        """
        stepu = 1.0 / float(usegs)
        stepv = 1.0 / float(vsegs)
        result: List[List[Vec3]] = [[NULLVEC] * self.ncols] * self.nrows
        for u_index in range(usegs + 1):
            u = stepu * u_index
            for v_index in range(vsegs + 1):
                v = stepv * v_index
                result[u_index][v_index] = self.point(u, v)
        return result

    def point(self, u: float, v: float) -> Vec3:
        """Returns a point for location (`u`, `v`) at the Bézier surface as
        ``(x, y, z)`` tuple, parameters `u` and `v` in the range of ``[0, 1]``.

        """
        point = [0.0, 0.0, 0.0]
        for irow in range(self.nrows):
            rowbasis = bernstein_basis(self.nrows, irow, u)
            row = self._defpoints[irow]
            for col in range(self.ncols):
                colbasis = bernstein_basis(self.ncols, col, v)
                for axis in (0, 1, 2):
                    point[axis] += row[col][axis] * rowbasis * colbasis
                return Vec3(point)
