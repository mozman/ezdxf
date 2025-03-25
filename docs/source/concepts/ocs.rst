.. _Object Coordinate System:

Object Coordinate System (OCS)
==============================


- `DXF Reference for OCS`_ provided by Autodesk.

The points associated with each entity are expressed in terms of the entity's
own object coordinate system (OCS). The OCS was referred to as ECS in previous
releases of AutoCAD.

With OCS, the only additional information needed to describe the entity's
position in 3D space is the 3D vector describing the z-axis of the OCS (often
referenced as extrusion vector), and the elevation value, which is the
distance of the entity xy-plane to the WCS/OCS origin.

For a given z-axis (extrusion) direction, there are an infinite number of
coordinate systems, defined by translating the origin in 3D space and by
rotating the x- and y-axis around the z-axis. However, for the same z-axis
direction, there is only one OCS. It has the following properties:

- Its origin coincides with the WCS origin.
- The orientation of the x- and y-axis within the xy-plane are calculated in an
  arbitrary but consistent manner. AutoCAD performs this calculation using the
  arbitrary axis algorithm (see below).
- Because of the `Arbitrary Axis Algorithm`_ the OCS can only represent a
  **right-handed** coordinate system!

The following entities do not lie in a particular plane. All points are
expressed in world coordinates. Of these entities, only lines and points can be
extruded. Their extrusion direction can differ from the world z-axis.

- :class:`~ezdxf.entities.Line`
- :class:`~ezdxf.entities.Point`
- :class:`~ezdxf.entities.3DFace`
- :class:`~ezdxf.entities.Polyline` (3D)
- :class:`~ezdxf.entities.Vertex` (3D)
- :class:`~ezdxf.entities.Polymesh`
- :class:`~ezdxf.entities.Polyface`
- :class:`~ezdxf.entities.Viewport`

These entities are planar in nature. All points are expressed in object
coordinates. All of these entities can be extruded. Their extrusion direction
can differ from the world z-axis.

- :class:`~ezdxf.entities.Circle`
- :class:`~ezdxf.entities.Arc`
- :class:`~ezdxf.entities.Solid`
- :class:`~ezdxf.entities.Trace`
- :class:`~ezdxf.entities.Text`
- :class:`~ezdxf.entities.Attrib`
- :class:`~ezdxf.entities.Attdef`
- :class:`~ezdxf.entities.Shape`
- :class:`~ezdxf.entities.Insert`
- :class:`~ezdxf.entities.Polyline` (2D)
- :class:`~ezdxf.entities.Vertex` (2D)
- :class:`~ezdxf.entities.LWPolyline`
- :class:`~ezdxf.entities.Hatch`
- :class:`~ezdxf.entities.Image`

Some of a :class:`~ezdxf.entities.Dimension`'s points are expressed in WCS and
some in OCS.

Elevation
---------

Elevation group code 38:

Exists only in output from versions prior to R11. Otherwise, Z coordinates are
supplied as part of each of the entity's defining points.

.. _Arbitrary Axis Algorithm:

Arbitrary Axis Algorithm
------------------------

- `DXF Reference for Arbitrary Axis Algorithm`_ provided by Autodesk.

The arbitrary axis algorithm is used by AutoCAD internally to implement the
arbitrary but consistent generation of object coordinate systems for all
entities that use object coordinates.

Given a unit-length vector to be used as the z-axis of a coordinate system, the
arbitrary axis algorithm generates a corresponding x-axis for the coordinate
system. The y-axis follows by application of the **right-hand** rule.

We are looking for the arbitrary x- and y-axis to go with the normal Az
(the arbitrary z-axis). They will be called Ax and Ay (using
:class:`~ezdxf.math.Vec3`):

.. code-block:: python

    Az = Vec3(entity.dxf.extrusion).normalize()  # normal (extrusion) vector
    if (abs(Az.x) < 1/64.) and (abs(Az.y) < 1/64.):
         Ax = Vec3(0, 1, 0).cross(Az).normalize()  # the cross-product operator
    else:
         Ax = Vec3(0, 0, 1).cross(Az).normalize()  # the cross-product operator
    Ay = Az.cross(Ax).normalize()


WCS to OCS
----------

.. code-block:: python

    def wcs_to_ocs(point):
        px, py, pz = Vec3(point)  # point in WCS
        x = px * Ax.x + py * Ax.y + pz * Ax.z
        y = px * Ay.x + py * Ay.y + pz * Ay.z
        z = px * Az.x + py * Az.y + pz * Az.z
        return Vec3(x, y, z)

OCS to WCS
----------

.. code-block:: python

    Wx = wcs_to_ocs((1, 0, 0))
    Wy = wcs_to_ocs((0, 1, 0))
    Wz = wcs_to_ocs((0, 0, 1))

    def ocs_to_wcs(point):
        px, py, pz = Vec3(point)  # point in OCS
        x = px * Wx.x + py * Wx.y + pz * Wx.z
        y = px * Wy.x + py * Wy.y + pz * Wy.z
        z = px * Wz.x + py * Wz.y + pz * Wz.z
        return Vec3(x, y, z)

.. seealso::

    - :class:`ezdxf.math.OCS` management class
    - The :meth:`ezdxf.entities.DXFGraphic.ocs` method returns the :class:`~ezdxf.math.OCS`
      of a graphical DXF entity.
    - :ref:`tut_ocs`

.. _DXF Reference for OCS: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-D99F1509-E4E4-47A3-8691-92EA07DC88F5

.. _DXF Reference for Arbitrary Axis Algorithm: https://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-E19E5B42-0CC7-4EBA-B29F-5E1D595149EE