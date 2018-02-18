# Copyright (c) 2012 Manfred Moitzi
# License: MIT License
from .bezier import bernstein_basis


class BezierSurface(object):
    def __init__(self, defpoints):
        """
        BezierSurface constructor

        Args:
            defpoints: defpoints is matrix (list of lists) of m rows and n columns.
            [ [m1n1, m1n2, ... ], [m2n1, m2n2, ...] ... ]
            each element is a 3D point (x, y, z) tuple or list

        """
        self._defpoints = defpoints
        self.nrows = len(defpoints)
        self.ncols = len(defpoints[0])

    def appoximate(self, usegs, vsegs):
        stepu = 1.0 / float(usegs)
        stepv = 1.0 / float(vsegs)
        result = [[0.0] * self.ncols] * self.nrows
        for ucounter in range(usegs+1):
            u = stepu * ucounter
            for vcounter in range(vsegs+1):
                v = stepv * vcounter
                result[u][v] = self.get_point(u, v)
        return result

    def get_point(self, u, v):
        """ u, v in range [0.0, 1.0].
        """
        point = [0.0, 0.0, 0.0]
        for irow in range(self.nrows):
            rowbasis = bernstein_basis(self.nrows, irow, u)
            row = self._defpoints[irow]
            for col in range(self.ncols):
                colbasis = bernstein_basis(self.ncols, col, v)
                for axis in (0, 1, 2):
                    point[axis] += row[col][axis] * rowbasis * colbasis
                return point
