.. module:: ezdxf.math

This classes located in module :mod:`ezdxf.math`::

    from ezdxf.math import OCS, UCS

OCS Class
---------

.. class:: OCS

.. method:: OCS.__init__(extrusion=(0, 0, 1))

    Establish an Object Coordinate System for a given extrusion vector.

.. method:: OCS.to_wcs(point)

    Calculate world coordinates for point in object coordinates.

.. method:: OCS.points_to_wcs(points)

    Translate multiple object coordinates into world coordinates (generator).

.. method:: OCS.from_wcs(point)

    Calculate object coordinates for point in world coordinates.

.. method:: OCS.points_from_wcs(points)

    Translate multiple world coordinates into object coordinates (generator).


.. seealso::

    :ref:`OCS`

UCS Class
---------

.. class:: UCS

.. method:: UCS.__init__(origin=(0, 0, 0), ux=None, uy=None, uz=None)

    Establish an User Coordinate System. The UCS is defined by the origin and two unit vectors for the x-, y- or
    z-axis, all axis n WCS. The missing axis is the cross product of the given axis.

    If x- and y-axis are None: ux=(1, 0, 0), uy=(0, 1, 0), uz=(0, 0, 1).

    Normalization of unit vectors is not required.

    :param origin: defines the UCS origin in world coordinates
    :param ux: defines the UCS x-axis as vector in :ref:`WCS`
    :param uy: defines the UCS y-axis as vector in :ref:`WCS`
    :param uz: defines the UCS z-axis as vector in :ref:`WCS`

.. method:: UCS.to_wcs(point)

    Calculate world coordinates for point in UCS coordinates.

.. method:: UCS.points_to_wcs(points)

    Translate multiple user coordinates into world coordinates (generator).

.. method:: UCS.to_ocs(point)

    Calculate :ref:`OCS` coordinates for point in UCS coordinates.

    OCS is defined by the z-axis of the UCS.

.. method:: UCS.to_ocs_angle_deg(angle)

    Transform angle in :ref:`UCS` xy-plane to angle in :ref:`OCS` xy-plane.

    OCS is defined by the z-axis of the UCS.

    :param float angle: angle in degrees
    :returns: OCS angle in degrees

.. method:: UCS.to_ocs_angle_rad(angle)

    Transform angle in :ref:`UCS` xy-plane to angle in :ref:`OCS` xy-plane.

    OCS is defined by the z-axis of the UCS.

    :param float angle: angle in radians
    :returns: OCS angle in radians

.. method:: UCS.points_from_wcs(points)

    Translate multiple user coordinates into :ref:`OCS` coordinates (generator).

    OCS is defined by the z-axis of the UCS.

.. method:: UCS.from_wcs(point)

    Calculate UCS coordinates for point in world coordinates.

.. method:: UCS.points_from_wcs(points)

    Translate multiple world coordinates into user coordinates (generator).

.. method:: UCS.from_x_axis_and_point_in_xy(origin, axis, point)

    Returns an new :class:`UCS` defined by the origin, the x-axis vector and an arbitrary point in the xy-plane. (static method)

    :param origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
    :param axis: x-axis vector as (x, y, z) tuple in :ref:`WCS`
    :param point: arbitrary point unlike the origin in the xy-plane as (x, y, z) tuple in :ref:`WCS`

.. method:: UCS.from_x_axis_and_point_in_xz(origin, axis, point)

    Returns an new :class:`UCS` defined by the origin, the x-axis vector and an arbitrary point in the xz-plane. (static method)

    :param origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
    :param axis: x-axis vector as (x, y, z) tuple in :ref:`WCS`
    :param point: arbitrary point unlike the origin in the xz-plane as (x, y, z) tuple in :ref:`WCS`

.. method:: UCS.from_y_axis_and_point_in_xy(origin, axis, point)

    Returns an new :class:`UCS` defined by the origin, the y-axis vector and an arbitrary point in the xy-plane. (static method)

    :param origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
    :param axis: y-axis vector as (x, y, z) tuple in :ref:`WCS`
    :param point: arbitrary point unlike the origin in the xy-plane as (x, y, z) tuple in :ref:`WCS`

.. method:: UCS.from_y_axis_and_point_in_yz(origin, axis, point)

    Returns an new :class:`UCS` defined by the origin, the y-axis vector and an arbitrary point in the yz-plane. (static method)

    :param origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
    :param axis: y-axis vector as (x, y, z) tuple in :ref:`WCS`
    :param point: arbitrary point unlike the origin in the yz-plane as (x, y, z) tuple in :ref:`WCS`

.. method:: UCS.from_z_axis_and_point_in_xz(origin, axis, point)

    Returns an new :class:`UCS` defined by the origin, the z-axis vector and an arbitrary point in the xz-plane. (static method)

    :param origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
    :param axis: z-axis vector as (x, y, z) tuple in :ref:`WCS`
    :param point: arbitrary point unlike the origin in the xz-plane as (x, y, z) tuple in :ref:`WCS`

.. method:: UCS.from_z_axis_and_point_in_yz(origin, axis, point)

    Returns an new :class:`UCS` defined by the origin, the z-axis vector and an arbitrary point in the yz-plane. (static method)

    :param origin: UCS origin as (x, y, z) tuple in :ref:`WCS`
    :param axis: z-axis vector as (x, y, z) tuple in :ref:`WCS`
    :param point: arbitrary point unlike the origin in the yz-plane as (x, y, z) tuple in :ref:`WCS`

.. seealso::

    :ref:`UCS`
