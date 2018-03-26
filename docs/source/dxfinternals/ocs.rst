.. _Object Coordinate System:

Object Coordinate System (OCS)
==============================


- `DXF Reference for OCS`_ provided by Autodesk.

The points associated with each entity are expressed in terms of the entity's own object coordinate system (OCS).
The OCS was referred to as ECS in previous releases of AutoCAD.

With OCS, the only additional information needed to describe the entity's position in 3D space is the 3D vector
describing the Z axis of the OCS, and the elevation value.

For a given Z axis (or extrusion) direction, there are an infinite number of coordinate systems, defined by translating
the origin in 3D space and by rotating the X and Y axes around the Z axis. However, for the same Z axis direction,
there is only one OCS. It has the following properties:

- Its origin coincides with the WCS origin.
- The orientation of the X and Y axes within the XY plane are calculated in an arbitrary but consistent manner. AutoCAD
  performs this calculation using the arbitrary axis algorithm.

These entities do not lie in a particular plane. All points are expressed in world coordinates. Of these entities,
only lines and points can be extruded. Their extrusion direction can differ from the world Z axis.

- :class:`Line`
- :class:`Point`
- :class:`3DFace`
- :class:`Polyline` (3D)
- :class:`Vertex` (3D)
- :class:`Polymesh`
- :class:`Polyface`
- :class:`Viewport`

These entities are planar in nature. All points are expressed in object coordinates. All of these entities can be
extruded. Their extrusion direction can differ from the world Z axis.

- :class:`Circle`
- :class:`Arc`
- :class:`Solid`
- :class:`Trace`
- :class:`Text`
- :class:`Attrib`
- :class:`Attdef`
- :class:`Shape`
- :class:`Insert`
- :class:`Polyline` (2D)
- :class:`Vertex` (2D)
- :class:`LWPolyline`
- :class:`Hatch`
- :class:`Image`

Some of a :class:`Dimension`'s points are expressed in WCS and some in OCS.

Elevation
---------

Elevation Group code 38:

Exists only in output from versions prior to R11. Otherwise, Z coordinates are supplied as part of each of the entity's
defining points.

Arbitrary Axis Algorithm
------------------------

- `DXF Reference for Arbitrary Axis Algorithm`_ provided by Autodesk.

The arbitrary axis algorithm is used by AutoCAD internally to implement the arbitrary but consistent generation of
object coordinate systems for all entities that use object coordinates.

Given a unit-length vector to be used as the Z axis of a coordinate system, the arbitrary axis algorithm generates a
corresponding X axis for the coordinate system. The Y axis follows by application of the right-hand rule.

We are looking for the arbitrary X and Y axes to go with the normal Az (the arbitrary Z axis).
They will be called Ax and Ay (using :class:`~ezdxf.algebra.Vector`)::

    Az = Vector(entity.dxf.extrusion).normalize()  # normal (extrusion) vector
    # Extrusion vector normalization should not be necessary, but don't rely on any DXF content
    if (abs(Az.x) < 1/64.) and (abs(Az.y) < 1/64.):
         Ax = Vector(0, 1, 0).cross(Az).normalize()  # the cross-product operator
    else:
         Ax = Vector(0, 0, 1).cross(Az).normalize()  # the cross-product operator
    Ay = Az.cross(Ax).normalize()


WCS to OCS
----------

.. code::

    def wcs_to_ocs(point):
        px, py, pz = Vector(point)  # point in WCS
        x = px * Ax.x + py * Ax.y + pz * Ax.z
        y = px * Ay.x + py * Ay.y + pz * Ay.z
        z = px * Az.x + py * Az.y + pz * Az.z
        return Vector(x, y, z)

OCS to WCS
----------

.. code::

    Wx = wcs_to_ocs((1, 0, 0))
    Wy = wcs_to_ocs((0, 1, 0))
    Wz = wcs_to_ocs((0, 0, 1))

    def ocs_to_wcs(point):
        px, py, pz = Vector(point)  # point in OCS
        x = px * Wx.x + py * Wx.y + pz * Wx.z
        y = px * Wy.x + py * Wy.y + pz * Wy.z
        z = px * Wz.x + py * Wz.y + pz * Wz.z
        return Vector(x, y, z)


.. _DXF Reference for OCS: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-D99F1509-E4E4-47A3-8691-92EA07DC88F5

.. _DXF Reference for Arbitrary Axis Algorithm: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-E19E5B42-0CC7-4EBA-B29F-5E1D595149EE