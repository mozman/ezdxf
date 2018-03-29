.. _tut_coordinates:

.. _tut_ocs:

Coordinates Tutorial
====================

First read the :ref:`Coordinate Systems` introduction please.

For :ref:`WCS` there is not much to say as, it is what it is: the main world coordinate system, and an a drawing unit can
have any real world unit you want. Autodesk added some mechanism to define a scale for dimension and text entities, but
because I am not an AutoCAD user, I am not familiar with it, and further more I think this is more an AutoCAD topic than
a DXF topic.

Object Coordinate System (OCS)
------------------------------

The :ref:`OCS` is used to place planar 2D entities in 3D space. **ALL** points of a planar entity lay in the same plane,
this is also true if the plane is located in 3D space by an OCS. There are three basic DXF attributes that gives a 2D
entity its spatial form.

Extrusion
~~~~~~~~~

The extrusion vector defines the OCS, it is a normal vector to the base plane of a planar entity. This `base plane` is
always located in the origin of the :ref:`WCS`. But there are some entities like :class:`Ellipse`, which have an
extrusion vector, but do not establish an OCS. For this entities the extrusion vector defines only the extrusion
direction and thickness defines the extrusion distance, but all other points in WCS.

Elevation
~~~~~~~~~

The elevation value defines the z-axis value for all points of a planar entity, this is an OCS value, and defines
the distance of the entity plane from the `base plane`.

This value exists only in output from DXF versions prior to R11 as separated DXF attribute (group code 38).
In DXF version R12 and later, the elevation value is supplied as z-axis value of each point. But as always in DXF, this
simple rule does not apply to all entities: :class:`LWPolyline` has an elevation attribute, :class:`Hatch` has an
elevation point (z=elevation , x=y=0), and so on.

Thickness
~~~~~~~~~

Defines the extrusion distance for an entity.

to be continued ...