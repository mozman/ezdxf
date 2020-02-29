# Copyright (c) 2018-2020 Manfred Moitzi
# License: MIT License
from typing import TYPE_CHECKING, Tuple, Sequence, Iterable, List, Union
from .vector import Vector, X_AXIS, Y_AXIS, Z_AXIS
from .matrix44 import Matrix44
from .matrix33 import Matrix33

if TYPE_CHECKING:
    from ezdxf.eztypes import Vertex, BaseLayout


def render_axis(layout: 'BaseLayout',
                start: 'Vertex',
                points: Sequence['Vertex'],
                colors: Tuple[int, int, int] = (1, 3, 5)) -> None:
    for point, color in zip(points, colors):
        layout.add_line(start, point, dxfattribs={'color': color})


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
        """ x-axis unit vector """
        return self.matrix.ux if self.transform else X_AXIS

    @property
    def uy(self) -> Vector:
        """ y-axis unit vector """
        return self.matrix.uy if self.transform else Y_AXIS

    @property
    def uz(self) -> Vector:
        """ z-axis unit vector """
        return self.matrix.uz if self.transform else Z_AXIS

    def from_wcs(self, point: 'Vertex') -> 'Vertex':
        """ Returns OCS vector for WCS `point`. """
        if self.transform:
            return self.transpose.transform(point)
        else:
            return point

    def points_from_wcs(self, points: Iterable['Vertex']) -> Iterable['Vertex']:
        """ Returns iterable of OCS vectors from WCS `points`. """
        for point in points:
            yield self.from_wcs(point)

    def to_wcs(self, point: 'Vertex') -> 'Vertex':
        """ Returns WCS vector for OCS `point`. """
        if self.transform:
            return self.matrix.transform(point)
        else:
            return point

    def points_to_wcs(self, points: Iterable['Vertex']) -> Iterable['Vertex']:
        """ Returns iterable of WCS vectors for OCS `points`. """
        for point in points:
            yield self.to_wcs(point)

    def render_axis(self, layout: 'BaseLayout', length: float = 1, colors: Tuple[int, int, int] = (1, 3, 5)):
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
    Establish an user coordinate system (:ref:`UCS`). The UCS is defined by the origin and two unit vectors for the x-,
    y- or z-axis, all axis in :ref:`WCS`. The missing axis is the cross product of the given axis.

    If x- and y-axis are ``None``: ux = ``(1, 0, 0)``, uy = ``(0, 1, 0)``, uz = ``(0, 0, 1)``.

    Unit vectors don't have to be normalized, normalization is done at initialization, this is also the reason why
    scaling gets lost by copying or rotating.

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
        self._setup(ux, uy, uz)

    def _setup(self, ux: Vector, uy: Vector, uz: Vector):
        self.matrix = Matrix33(ux, uy, uz)
        self.transpose = self.matrix.transpose()

    @property
    def ux(self) -> Vector:
        """ x-axis unit vector """
        return self.matrix.ux

    @property
    def uy(self) -> Vector:
        """ y-axis unit vector """
        return self.matrix.uy

    @property
    def uz(self) -> Vector:
        """ z-axis unit vector """
        return self.matrix.uz

    def copy(self) -> 'UCS':
        """ Returns a copy of this UCS.

        .. versionadded:: 0.11

        """
        return UCS(self.origin, self.ux, self.uy, self.uz)

    def scale(self, sx: float = 1, sy: float = 1, sz: float = 1) -> 'UCS':
        """ Returns a new scaled UCS.

        Scaling gets lost by rotating or copying the UCS, because this operations crates a new UCS and unit
        vectors always get normalized on initialization.

        Args:
            sx: x-axis scaling
            sy: y-axis scaling
            sz: z-axis scaling

        """
        ucs = self.copy()
        ucs._setup(self.ux * sx, self.uy * sy, self.uz * sz)
        return ucs

    def to_wcs(self, point: 'Vertex') -> 'Vector':
        """ Returns WCS point for UCS `point`. """
        return self.origin + self.matrix.transform(point)

    def points_to_wcs(self, points: Iterable['Vertex']) -> Iterable['Vector']:
        """ Returns iterable of WCS vectors for UCS `points`. """
        for point in points:
            yield self.to_wcs(point)

    def direction_to_wcs(self, vector: 'Vertex') -> 'Vector':
        """ Returns WCS direction for UCS `vector` without origin adjustment. """
        return self.matrix.transform(vector)

    def from_wcs(self, point: 'Vertex') -> 'Vector':
        """ Returns UCS point for WCS `point`. """
        return self.transpose.transform(point - self.origin)

    def points_from_wcs(self, points: Iterable['Vertex']) -> Iterable['Vector']:
        """ Returns iterable of UCS vectors from WCS `points`. """
        for point in points:
            yield self.from_wcs(point)

    def direction_from_wcs(self, vector: 'Vertex') -> 'Vector':
        """ Returns UCS vector for WCS `vector` without origin adjustment. """
        return self.transpose.transform(vector)

    def to_ocs(self, point: 'Vertex') -> 'Vector':
        """
        Returns OCS vector for UCS `point`.

        The :class:`OCS` is defined by the z-axis of the :class:`UCS`.

        """
        wpoint = self.to_wcs(point)
        return OCS(self.uz).from_wcs(wpoint)

    def points_to_ocs(self, points: Iterable['Vertex']) -> Iterable['Vector']:
        """
        Returns iterable of OCS vectors for UCS `points`.

        The :class:`OCS` is defined by the z-axis of the :class:`UCS`.

        Args:
            points: iterable of UCS vertices

        """
        wcs = self.to_wcs
        ocs = OCS(self.uz)
        for point in points:
            yield ocs.from_wcs(wcs(point))

    def ocs_points_to_ocs(self, points: Iterable['Vertex'], extrusion=Z_AXIS) -> Iterable['Vector']:
        """
        Returns iterable of OCS vectors for UCS `points` located by an OCS established by
        the `extrusion` vector.

        Args:
            points: iterable of UCS vertices located in an OCS
            extrusion: vector defines the source OCS

        """
        if Z_AXIS.isclose(extrusion):
            yield from self.points_to_ocs(points)
        else:
            source_ocs = OCS(extrusion)
            ocs_to_ucs = source_ocs.to_wcs
            ucs_points = (ocs_to_ucs(p) for p in points)

            wcs = self.to_wcs
            target_ocs = OCS(self.direction_to_wcs(extrusion))
            ocs_from_wcs = target_ocs.from_wcs
            for point in ucs_points:
                yield ocs_from_wcs(wcs(point))

    def to_ocs_angle_deg(self, angle: float) -> float:
        """
        Transforms `angle` from current UCS to the parent coordinate system (most likely the WCS) including
        the transformation to the OCS established by the extrusion vector :attr:`UCS.uz`.

        Args:
            angle: in UCS in degrees

        """
        return self.ucs_direction_to_ocs_direction(Vector.from_deg_angle(angle)).angle_deg

    def angles_to_ocs_deg(self, angles: Iterable[float]) -> List[float]:
        """
        Transforms `angles` from current UCS to the parent coordinate system (most likely the WCS) including
        the transformation to the OCS established by the extrusion vector :attr:`UCS.uz`.

        Args:
            angles: iterable of UCS (OCS) angles to transform, angles in degrees

        Returns:
            List of OCS angles in degrees.

        """
        # Convert angles to direction vectors
        directions = self.ucs_directions_to_ocs_directions(
            directions=(Vector.from_deg_angle(a) for a in angles),
            extrusion=Z_AXIS,
        )
        return [vector.angle_deg for vector in directions]

    def ocs_angles_to_ocs_deg(self, angles: Iterable[float], extrusion=Z_AXIS) -> List[float]:
        """
        Transforms `angles` from current UCS located in an established OCS defined by the given `extrusion` vector
        to the parent coordinate system (most likely the WCS) including the transformation to the target OCS established
        by the transformed `extrusion` vector.

        Args:
            angles: iterable of UCS (OCS) angles to transform, angles in degrees
            extrusion: extrusion vector of the source OCS

        Returns:
            List of OCS angles in degrees.

        """

        if Z_AXIS.isclose(extrusion):
            return self.angles_to_ocs_deg(angles)

        ocs = OCS(extrusion)
        ocs_to_wcs = ocs.to_wcs
        # Convert angles to direction vectors
        directions = self.ucs_directions_to_ocs_directions(
            directions=(ocs_to_wcs(Vector.from_deg_angle(a)) for a in angles),
            extrusion=extrusion,
        )
        return [vector.angle_deg for vector in directions]

    def ucs_direction_to_ocs_direction(self, direction: Vector) -> Vector:
        """
        Transforms UCS `direction` vector into OCS direction vector of the parent coordinate system (most likely
        the WCS), target OCS is defined by the UCS z-axis.
        """
        return OCS(self.uz).from_wcs(self.direction_to_wcs(direction))

    def ucs_directions_to_ocs_directions(self, directions: Iterable[Vector], extrusion: Vector) -> Iterable[Vector]:
        """
        Transforms UCS direction vectors into OCS direction vectors of the parent coordinate system (most likely
        the WCS), target OCS is defined by the `extrusion` vector.

        Args:
            directions: iterable of UCS directions
            extrusion: extrusion vector of the target OCS

        Returns:
            Iterable of OCS directions as vectors.

        """
        # Transform UCS directions to PCS (Parent Coordinate System), most likely the WCS
        ucs_to_pcs = self.direction_to_wcs
        pcs_directions = (ucs_to_pcs(v) for v in directions)

        # Convert PCS direction to OCS established by transformed extrusion vector
        target_ocs = OCS(self.direction_to_wcs(extrusion))
        ocs_from_pcs = target_ocs.from_wcs
        return (ocs_from_pcs(v) for v in pcs_directions)

    def rotate(self, axis: 'Vertex', angle: float) -> 'UCS':
        """
        Returns a new rotated UCS, with the same origin as the source UCS.
        The rotation vector is located in the origin and has :ref:`WCS` coordinates e.g. (0, 0, 1) is the WCS z-axis
        as rotation vector.

        Scaling get lost because creates new UCS and unit vectors always get normalized on initialization.

        .. versionadded:: 0.11

        Args:
            axis: arbitrary rotation axis as vector in :ref:`WCS`
            angle: rotation angle in radians

        """
        t = Matrix44.axis_rotate(Vector(axis), angle)
        ux, uy, uz = t.transform_vectors([self.ux, self.uy, self.uz])
        return UCS(origin=self.origin, ux=ux, uy=uy, uz=uz)

    def rotate_local_x(self, angle: float) -> 'UCS':
        """
        Returns a new rotated UCS, rotation axis is the local x-axis.

        Scaling get lost because creates new UCS and unit vectors always get normalized on initialization.

        .. versionadded:: 0.11

        Args:
             angle: rotation angle in radians

        """
        t = Matrix44.axis_rotate(self.ux, angle)
        uy, uz = t.transform_vectors([self.uy, self.uz])
        return UCS(origin=self.origin, ux=self.ux, uy=uy, uz=uz)

    def rotate_local_y(self, angle: float) -> 'UCS':
        """
        Returns a new rotated UCS, rotation axis is the local y-axis.

        Scaling get lost because creates new UCS and unit vectors always get normalized on initialization.

        .. versionadded:: 0.11

        Args:
             angle: rotation angle in radians

        """
        t = Matrix44.axis_rotate(self.uy, angle)
        ux, uz = t.transform_vectors([self.ux, self.uz])
        return UCS(origin=self.origin, ux=ux, uy=self.uy, uz=uz)

    def rotate_local_z(self, angle: float) -> 'UCS':
        """
        Returns a new rotated UCS, rotation axis is the local z-axis.

        Scaling get lost because creates new UCS and unit vectors always get normalized on initialization.

        .. versionadded:: 0.11

        Args:
             angle: rotation angle in radians

        """
        t = Matrix44.axis_rotate(self.uz, angle)
        ux, uy = t.transform_vectors([self.ux, self.uy])
        return UCS(origin=self.origin, ux=ux, uy=uy, uz=self.uz)

    def shift(self, delta: 'Vertex') -> 'UCS':
        """
        Shifts current UCS by `delta` vector and returns `self`.

        .. versionadded:: 0.11

        Args:
            delta: shifting vector

        """
        self.origin += Vector(delta)
        return self

    def moveto(self, location: 'Vertex') -> 'UCS':
        """
        Place current UCS at new origin `location` and returns `self`.

        .. versionadded:: 0.11

        Args:
            location: new origin in WCS

        """
        self.origin = Vector(location)
        return self

    @property
    def is_cartesian(self) -> bool:
        """ Returns ``True`` if cartesian coordinate system. """
        return self.uy.cross(self.uz).normalize().isclose(self.ux.normalize())

    @staticmethod
    def from_x_axis_and_point_in_xy(origin: 'Vertex', axis: 'Vertex', point: 'Vertex') -> 'UCS':
        """
        Returns an new :class:`UCS` defined by the origin, the x-axis vector and an arbitrary point in the xy-plane.

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

    def render_axis(self, layout: 'BaseLayout', length: float = 1, colors: Tuple[int, int, int] = (1, 3, 5)):
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
