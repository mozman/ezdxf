# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from .vector import Vector
from .matrix import Matrix


class OCS(object):
    _Ax = Vector(1, 0, 0)
    _Ay = Vector(0, 1, 0)
    _Az = Vector(0, 0, 1)

    def __init__(self, extrusion=(0, 0, 1)):
        self.transform = extrusion != (0, 0, 1)
        if self.transform:
            Az = Vector(extrusion).normalize()
            if (abs(Az.x) < 1/64.) and (abs(Az.y) < 1/64.):
                Ax = Vector(0, 1, 0).cross(Az)
            else:
                Ax = Vector(0, 0, 1).cross(Az)
            Ax = Ax.normalize()
            Ay = Az.cross(Ax).normalize()
            self.matrix = Matrix.setup_ucs_transform(Ax, Ay, Az)
            self.transpose = self.matrix.transpose()

    @property
    def ux(self):
        return Vector(self.matrix.row(0)) if self.transform else self._Ax

    @property
    def uy(self):
        return Vector(self.matrix.row(1)) if self.transform else self._Ay

    @property
    def uz(self):
        return Vector(self.matrix.row(2)) if self.transform else self._Az

    def wcs_to_ocs(self, point):
        if self.transform:
            return self.matrix.fast_ucs_transform(point)
        else:
            return point

    def points_to_ocs(self, points):
        for point in points:
            yield self.wcs_to_ocs(point)

    def ocs_to_wcs(self, point):
        if self.transform:
            return self.transpose.fast_ucs_transform(point)
        else:
            return point

    def points_to_wcs(self, points):
        for point in points:
            yield self.ocs_to_wcs(point)


class UCS(object):
    def __init__(self, origin=(0, 0, 0), ux=(1, 0, 0), uy=(0, 1, 0)):
        self.origin = Vector(origin)
        ux = Vector(ux).normalize()
        uy = Vector(uy).normalize()
        uz = Vector(ux).cross(uy).normalize()
        self.matrix = Matrix.setup_ucs_transform(ux, uy, uz)
        self.transpose = self.matrix.transpose()

    @property
    def ux(self):
        return Vector(self.matrix.row(0))

    @property
    def uy(self):
        return Vector(self.matrix.row(1))

    @property
    def uz(self):
        return Vector(self.matrix.row(2))

    def ucs_to_wcs(self, point):
        return self.origin + self.matrix.fast_ucs_transform(point)

    def points_to_wcs(self, points):
        for point in points:
            yield self.ucs_to_wcs(point)

    def wcs_to_ucs(self, point):
        return self.transpose.fast_ucs_transform(point - self.origin)

    def points_to_ucs(self, points):
        for point in points:
            yield self.wcs_to_ucs(point)

    @property
    def is_cartesian(self):
        return self.uy.cross(self.uz).is_almost_equal(self.ux)
