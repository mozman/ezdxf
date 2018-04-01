# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from .vector import Vector, X_AXIS, Y_AXIS, Z_AXIS


def render_axis(layout, start, points, colors=(1, 3, 5)):
    for point, color in zip(points, colors):
        layout.add_line(start, point, dxfattribs={'color': color})


class Matrix33(object):
    """
    Simple 3x3 Matrix for coordinate transformation.

    """
    __slots__ = ('ux', 'uy', 'uz')

    def __init__(self, ux=(1, 0, 0), uy=(0, 1, 0), uz=(0, 0, 1)):
        self.ux = Vector(ux)
        self.uy = Vector(uy)
        self.uz = Vector(uz)

    def transpose(self):
        return Matrix33(
            (self.ux.x, self.uy.x, self.uz.x),
            (self.ux.y, self.uy.y, self.uz.y),
            (self.ux.z, self.uy.z, self.uz.z),
        )

    def transform(self, vector):
        px, py, pz = Vector(vector)
        ux = self.ux
        uy = self.uy
        uz = self.uz
        x = px * ux.x + py * uy.x + pz * uz.x
        y = px * ux.y + py * uy.y + pz * uz.y
        z = px * ux.z + py * uy.z + pz * uz.z
        return Vector(x, y, z)


class OCS(object):
    def __init__(self, extrusion=Z_AXIS):
        Az = Vector(extrusion).normalize()
        self.transform = not Az.is_almost_equal(Z_AXIS)
        if self.transform:
            if (abs(Az.x) < 1 / 64.) and (abs(Az.y) < 1 / 64.):
                Ax = Y_AXIS.cross(Az)
            else:
                Ax = Z_AXIS.cross(Az)
            Ax = Ax.normalize()
            Ay = Az.cross(Ax).normalize()
            self.matrix = Matrix33(Ax, Ay, Az)
            self.transpose = self.matrix.transpose()

    @property
    def ux(self):
        return self.matrix.ux if self.transform else X_AXIS

    @property
    def uy(self):
        return self.matrix.uy if self.transform else Y_AXIS

    @property
    def uz(self):
        return self.matrix.uz if self.transform else Z_AXIS

    def wcs_to_ocs(self, point):
        if self.transform:
            return self.transpose.transform(point)
        else:
            return point

    def points_to_ocs(self, points):
        for point in points:
            yield self.wcs_to_ocs(point)

    def ocs_to_wcs(self, point):
        if self.transform:
            return self.matrix.transform(point)
        else:
            return point

    def points_to_wcs(self, points):
        for point in points:
            yield self.ocs_to_wcs(point)

    def render_axis(self, layout, length=1, colors=(1, 3, 5)):
        render_axis(
            layout,
            start=(0, 0, 0),
            points=(
                self.ocs_to_wcs(X_AXIS * length),
                self.ocs_to_wcs(Y_AXIS * length),
                self.ocs_to_wcs(Z_AXIS * length),
            ),
            colors=colors,
        )


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

        self.matrix = Matrix33(ux, uy, uz)
        self.transpose = self.matrix.transpose()

    @property
    def ux(self):
        return self.matrix.ux

    @property
    def uy(self):
        return self.matrix.uy

    @property
    def uz(self):
        return self.matrix.uz

    def ucs_to_wcs(self, point):
        """
        Calculate world coordinates for point in UCS coordinates.

        """
        return self.origin + self.matrix.transform(point)

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
        return self.transpose.transform(point - self.origin)

    def points_to_ucs(self, points):
        """
        Translate multiple world coordinates into user coordinates (generator).

        """
        for point in points:
            yield self.wcs_to_ucs(point)

    @property
    def is_cartesian(self):
        return self.uy.cross(self.uz).is_almost_equal(self.ux)

    @staticmethod
    def from_x_axis_and_point_in_xy(origin, axis, point):
        x_axis = Vector(axis)
        z_axis = x_axis.cross(Vector(point) - origin)
        return UCS(origin=origin, ux=x_axis, uz=z_axis)

    @staticmethod
    def from_x_axis_and_point_in_xz(origin, axis, point):
        x_axis = Vector(axis)
        xz_vector = Vector(point) - origin
        y_axis = xz_vector.cross(x_axis)
        return UCS(origin=origin, ux=x_axis, uy=y_axis)

    @staticmethod
    def from_y_axis_and_point_in_xy(origin, axis, point):
        y_axis = Vector(axis)
        xy_vector = Vector(point) - origin
        z_axis = xy_vector.cross(y_axis)
        return UCS(origin=origin, uy=y_axis, uz=z_axis)

    @staticmethod
    def from_y_axis_and_point_in_yz(origin, axis, point):
        y_axis = Vector(axis)
        yz_vector = Vector(point) - origin
        x_axis = yz_vector.cross(y_axis)
        return UCS(origin=origin, ux=x_axis, uy=y_axis)

    @staticmethod
    def from_z_axis_and_point_in_xz(origin, axis, point):
        z_axis = Vector(axis)
        y_axis = z_axis.cross(Vector(point) - origin)
        return UCS(origin=origin, uy=y_axis, uz=z_axis)

    @staticmethod
    def from_z_axis_and_point_in_yz(origin, axis, point):
        z_axis = Vector(axis)
        yz_vector = Vector(point) - origin
        x_axis = yz_vector.cross(z_axis)
        return UCS(origin=origin, ux=x_axis, uz=z_axis)

    def render_axis(self, layout, length=1, colors=(1, 3, 5)):
        render_axis(
            layout,
            start=self.origin,
            points=(
                self.ucs_to_wcs(X_AXIS * length),
                self.ucs_to_wcs(Y_AXIS * length),
                self.ucs_to_wcs(Z_AXIS * length),
            ),
            colors=colors,
        )
