# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from .vector import Vector, X_AXIS, Y_AXIS, Z_AXIS
from .matrix import Matrix


class OCS(object):
    def __init__(self, extrusion=Z_AXIS):
        self.transform = extrusion != Z_AXIS
        if self.transform:
            Az = Vector(extrusion).normalize()
            if (abs(Az.x) < 1/64.) and (abs(Az.y) < 1/64.):
                Ax = Y_AXIS.cross(Az)
            else:
                Ax = Z_AXIS.cross(Az)
            Ax = Ax.normalize()
            Ay = Az.cross(Ax).normalize()
            self.matrix = Matrix.setup_ucs_transform(Ax, Ay, Az)
            self.transpose = self.matrix.transpose()

    @property
    def ux(self):
        return Vector(self.matrix.row(0)) if self.transform else X_AXIS

    @property
    def uy(self):
        return Vector(self.matrix.row(1)) if self.transform else Y_AXIS

    @property
    def uz(self):
        return Vector(self.matrix.row(2)) if self.transform else Z_AXIS

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
    def __init__(self, origin=(0, 0, 0), ux=None, uy=None, uz=None):
        self.origin = Vector(origin)
        if ux is None and uy is None:
            ux = X_AXIS
            uy = Y_AXIS
            uz = Z_AXIS
        elif ux is None:
            uy = Vector(uy).normalize()
            uz = Vector(uz).normalize()
            ux = Vector(uy).cross(uz).normalize()
        elif uy is None:
            ux = Vector(ux).normalize()
            uz = Vector(uz).normalize()
            uy = Vector(uz).cross(ux).normalize()
        elif uz is None:
            ux = Vector(ux).normalize()
            uy = Vector(uy).normalize()
            uz = Vector(ux).cross(uy).normalize()
        else:  # all axis are given
            ux = Vector(ux).normalize()
            uy = Vector(uy).normalize()
            uz = Vector(uz).normalize()

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
        """
        Calculate world coordinates for point in UCS coordinates.

        """
        return self.origin + self.matrix.fast_ucs_transform(point)

    def points_to_wcs(self, points):
        """
        Translate multiple user coordinates into world coordinates (generator).

        """
        for point in points:
            yield self.ucs_to_wcs(point)

    def ucs_to_ocs(self, point):
        """
        Calculate OCS coordinates for point in UCS coordinates.

        OCS is defined by the z-axis of the UCS.

        """
        wpoint = self.ucs_to_wcs(point)
        return OCS(self.uz).wcs_to_ocs(wpoint)

    def points_to_ocs(self, points):
        """
        Translate multiple user coordinates into OCS coordinates (generator).

        OCS is defined by the z-axis of the UCS.

        """
        wcs = self.ucs_to_wcs
        ocs = OCS(self.uz)
        for point in points:
            yield ocs.wcs_to_ocs(wcs(point))

    def wcs_to_ucs(self, point):
        """
        Calculate UCS coordinates for point in world coordinates.

        """
        return self.transpose.fast_ucs_transform(point - self.origin)

    def points_to_ucs(self, points):
        """
        Translate multiple world coordinates into user coordinates (generator).

        """
        for point in points:
            yield self.wcs_to_ucs(point)

    @property
    def is_cartesian(self):
        return self.uy.cross(self.uz).is_almost_equal(self.ux)
