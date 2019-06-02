# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple, Sequence, Iterable
from .vector import Vector, X_AXIS, Y_AXIS, Z_AXIS

if TYPE_CHECKING:
    from ezdxf.eztypes import GenericLayoutType, Vertex


def render_axis(layout: 'GenericLayoutType',
                start: 'Vertex',
                points: Sequence['Vertex'],
                colors: Tuple[int, int, int] = (1, 3, 5)) -> None:
    for point, color in zip(points, colors):
        layout.add_line(start, point, dxfattribs={'color': color})


class Matrix33:
    """
    Simple 3x3 Matrix for coordinate transformation.

    """
    __slots__ = ('ux', 'uy', 'uz')

    def __init__(self, ux: 'Vertex' = (1, 0, 0), uy: 'Vertex' = (0, 1, 0), uz: 'Vertex' = (0, 0, 1)):
        self.ux = Vector(ux)
        self.uy = Vector(uy)
        self.uz = Vector(uz)

    def transpose(self) -> 'Matrix33':
        return Matrix33(
            (self.ux.x, self.uy.x, self.uz.x),
            (self.ux.y, self.uy.y, self.uz.y),
            (self.ux.z, self.uy.z, self.uz.z),
        )

    def transform(self, vector: 'Vertex') -> Vector:
        px, py, pz = Vector(vector)
        ux = self.ux
        uy = self.uy
        uz = self.uz
        x = px * ux.x + py * uy.x + pz * uz.x
        y = px * ux.y + py * uy.y + pz * uz.y
        z = px * ux.z + py * uy.z + pz * uz.z
        return Vector(x, y, z)


class OCS:
    """
    Establish an :ref:`OCS` for a given extrusion vector.

    Args:
        extrusion: extrusion vector.
    """

    def __init__(self, extrusion: 'Vertex' = Z_AXIS):
        Az = Vector(extrusion).normalize()
        self.transform = not Az.isclose(Z_AXIS)
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
    def ux(self) -> Vector:
        """ x unit vector """
        return self.matrix.ux if self.transform else X_AXIS

    @property
    def uy(self) -> Vector:
        """ y unit vector """
        return self.matrix.uy if self.transform else Y_AXIS

    @property
    def uz(self) -> Vector:
        """ z unit vector """
        return self.matrix.uz if self.transform else Z_AXIS

    def from_wcs(self, point: 'Vertex') -> 'Vertex':
        """ Calculate object coordinates for point in world coordinates.
        """
        if self.transform:
            return self.transpose.transform(point)
        else:
            return point

    def points_from_wcs(self, points: Iterable['Vertex']) -> Iterable['Vertex']:
        """ Translate multiple world coordinates into object coordinates (generator).
        """
        for point in points:
            yield self.from_wcs(point)

    def to_wcs(self, point: 'Vertex') -> 'Vertex':
        """ Calculate world coordinates for point in object coordinates.
        """
        if self.transform:
            return self.matrix.transform(point)
        else:
            return point

    def points_to_wcs(self, points: Iterable['Vertex']) -> Iterable['Vertex']:
        """ Translate multiple object coordinates into world coordinates (generator).
        """
        for point in points:
            yield self.to_wcs(point)

    def render_axis(self, layout: 'GenericLayoutType', length: float = 1, colors: Tuple[int, int, int] = (1, 3, 5)):
        """ Render axis as 3D lines into a `layout`. """
        render_axis(
            layout,
            start=(0, 0, 0),
            points=(
                self.to_wcs(X_AXIS * length),
                self.to_wcs(Y_AXIS * length),
                self.to_wcs(Z_AXIS * length),
            ),
            colors=colors,
        )


class UCS:
    """
    Establish an User Coordinate System (:ref:`UCS`). The UCS is defined by the origin and two unit vectors for the x-,
    y- or z-axis, all axis in :ref:`WCS`. The missing axis is the cross product of the given axis.

    If x- and y-axis are None: ux=(1, 0, 0), uy=(0, 1, 0), uz=(0, 0, 1).

    Normalization of unit vectors is not required.

    Args:
        origin: defines the UCS origin in world coordinates
        ux: defines the UCS x-axis as vector in :ref:`WCS`
        uy: defines the UCS y-axis as vector in :ref:`WCS`
        uz: defines the UCS z-axis as vector in :ref:`WCS`

    """

    def __init__(self, origin: 'Vertex' = (0, 0, 0), ux: 'Vertex' = None, uy: 'Vertex' = None, uz: 'Vertex' = None):
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
    def ux(self) -> Vector:
        """ x unit vector """
        return self.matrix.ux

    @property
    def uy(self) -> Vector:
        """ y unit vector """
        return self.matrix.uy

    @property
    def uz(self) -> Vector:
        """ z unit vector """
        return self.matrix.uz

    def to_wcs(self, point: 'Vertex') -> 'Vector':
        """
        Calculate world coordinates for point in UCS coordinates.

        """
        return self.origin + self.matrix.transform(point)

    def points_to_wcs(self, points: Iterable['Vertex']) -> Iterable['Vector']:
        """
        Translate multiple user coordinates into world coordinates (generator).

        """
        for point in points:
            yield self.to_wcs(point)

    def to_ocs(self, point: 'Vertex') -> 'Vertex':
        """
        Calculate OCS coordinates for point in UCS coordinates.

        OCS is defined by the z-axis of the UCS.

        """
        wpoint = self.to_wcs(point)
        return OCS(self.uz).from_wcs(wpoint)

    def points_to_ocs(self, points: Iterable['Vertex']) -> Iterable['Vertex']:
        """
        Translate multiple user coordinates into OCS coordinates (generator).

        OCS is defined by the z-axis of the UCS.

        """
        wcs = self.to_wcs
        ocs = OCS(self.uz)
        for point in points:
            yield ocs.from_wcs(wcs(point))

    def to_ocs_angle_deg(self, angle: float) -> float:
        """
        Transform angle in UCS xy-plane to angle in OCS xy-plane.

        Args:
            angle: in UCS in degrees

        Returns: angle in OCS in degrees

        """
        vec = Vector.from_deg_angle(angle)
        vec = self.to_ocs(vec) - self.origin
        return vec.angle_deg

    def to_ocs_angle_rad(self, angle: float) -> float:
        """
        Transform angle in UCS xy-plane to angle in OCS xy-plane.

        Args:
            angle: in UCS in radians

        Returns: angle in OCS in radians

        """
        vec = Vector.from_angle(angle)
        vec = self.to_ocs(vec) - self.origin
        return vec.angle

    def from_wcs(self, point: 'Vertex') -> 'Vector':
        """
        Calculate UCS coordinates for point in world coordinates.

        """
        return self.transpose.transform(point - self.origin)

    def points_from_wcs(self, points: Iterable['Vertex']) -> Iterable['Vector']:
        """
        Translate multiple world coordinates into user coordinates (generator).

        """
        for point in points:
            yield self.from_wcs(point)

    @property
    def is_cartesian(self) -> bool:
        """ True if cartesian coordinate system """
        return self.uy.cross(self.uz).isclose(self.ux)

    @staticmethod
    def from_x_axis_and_point_in_xy(origin: 'Vertex', axis: 'Vertex', point: 'Vertex') -> 'UCS':
        """ Returns an new :class:`UCS` defined by the origin, the x-axis vector and an arbitrary point in the xy-plane.

        Args:
            origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
            axis: x-axis vector as (x, y, z) tuple in :ref:`WCS`
            point: arbitrary point unlike the origin in the xy-plane as (x, y, z) tuple in :ref:`WCS`

        """
        x_axis = Vector(axis)
        z_axis = x_axis.cross(Vector(point) - origin)
        return UCS(origin=origin, ux=x_axis, uz=z_axis)

    @staticmethod
    def from_x_axis_and_point_in_xz(origin: 'Vertex', axis: 'Vertex', point: 'Vertex') -> 'UCS':
        """
        Returns an new :class:`UCS` defined by the origin, the x-axis vector and an arbitrary point in the xz-plane.

        Args:
            origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
            axis: x-axis vector as (x, y, z) tuple in :ref:`WCS`
            point: arbitrary point unlike the origin in the xz-plane as (x, y, z) tuple in :ref:`WCS`

        """
        x_axis = Vector(axis)
        xz_vector = Vector(point) - origin
        y_axis = xz_vector.cross(x_axis)
        return UCS(origin=origin, ux=x_axis, uy=y_axis)

    @staticmethod
    def from_y_axis_and_point_in_xy(origin: 'Vertex', axis: 'Vertex', point: 'Vertex') -> 'UCS':
        """
        Returns an new :class:`UCS` defined by the origin, the y-axis vector and an arbitrary point in the xy-plane.

        Args:
            origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
            axis: y-axis vector as (x, y, z) tuple in :ref:`WCS`
            point: arbitrary point unlike the origin in the xy-plane as (x, y, z) tuple in :ref:`WCS`

        """
        y_axis = Vector(axis)
        xy_vector = Vector(point) - origin
        z_axis = xy_vector.cross(y_axis)
        return UCS(origin=origin, uy=y_axis, uz=z_axis)

    @staticmethod
    def from_y_axis_and_point_in_yz(origin: 'Vertex', axis: 'Vertex', point: 'Vertex') -> 'UCS':
        """
        Returns an new :class:`UCS` defined by the origin, the y-axis vector and an arbitrary point in the yz-plane.

        Args:
            origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
            axis: y-axis vector as (x, y, z) tuple in :ref:`WCS`
            point: arbitrary point unlike the origin in the yz-plane as (x, y, z) tuple in :ref:`WCS`

        """
        y_axis = Vector(axis)
        yz_vector = Vector(point) - origin
        x_axis = yz_vector.cross(y_axis)
        return UCS(origin=origin, ux=x_axis, uy=y_axis)

    @staticmethod
    def from_z_axis_and_point_in_xz(origin: 'Vertex', axis: 'Vertex', point: 'Vertex') -> 'UCS':
        """
        Returns an new :class:`UCS` defined by the origin, the z-axis vector and an arbitrary point in the xz-plane.

        Args:
            origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
            axis: z-axis vector as (x, y, z) tuple in :ref:`WCS`
            point: arbitrary point unlike the origin in the xz-plane as (x, y, z) tuple in :ref:`WCS`

        """
        z_axis = Vector(axis)
        y_axis = z_axis.cross(Vector(point) - origin)
        return UCS(origin=origin, uy=y_axis, uz=z_axis)

    @staticmethod
    def from_z_axis_and_point_in_yz(origin: 'Vertex', axis: 'Vertex', point: 'Vertex') -> 'UCS':
        """
        Returns an new :class:`UCS` defined by the origin, the z-axis vector and an arbitrary point in the yz-plane.

        Args:
            origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
            axis: z-axis vector as (x, y, z) tuple in :ref:`WCS`
            point: arbitrary point unlike the origin in the yz-plane as (x, y, z) tuple in :ref:`WCS`

        """
        z_axis = Vector(axis)
        yz_vector = Vector(point) - origin
        x_axis = yz_vector.cross(z_axis)
        return UCS(origin=origin, ux=x_axis, uz=z_axis)

    def render_axis(self, layout: 'GenericLayoutType', length: float = 1, colors: Tuple[int, int, int] = (1, 3, 5)):
        """ Render axis as 3D lines into a `layout`. """
        render_axis(
            layout,
            start=self.origin,
            points=(
                self.to_wcs(X_AXIS * length),
                self.to_wcs(Y_AXIS * length),
                self.to_wcs(Z_AXIS * length),
            ),
            colors=colors,
        )


class PassTroughUCS(UCS):
    """ UCS is equal to the WCS and OCS (extrusion = 0, 0, 1) """

    def __init__(self):
        super().__init__()

    def to_wcs(self, point: 'Vertex') -> Vector:
        return Vector(point)

    def points_to_wcs(self, points: Iterable['Vertex']) -> Iterable[Vector]:
        for point in points:
            yield Vector(point)

    def to_ocs(self, point: 'Vertex') -> 'Vertex':
        return Vector(point)

    def points_to_ocs(self, points: Iterable['Vertex']) -> Iterable['Vertex']:
        for point in points:
            yield Vector(point)

    def to_ocs_angle_deg(self, angle: float) -> float:
        return angle

    def to_ocs_angle_rad(self, angle: float) -> float:
        return angle

    def from_wcs(self, point: 'Vertex') -> Vector:
        return Vector(point)

    def points_from_wcs(self, points: Iterable['Vertex']) -> Iterable[Vector]:
        for point in points:
            yield Vector(point)
