Surface
=======

.. class:: Surface(Body)

Introduced in DXF version R13 (AC1012), dxftype is SURFACE.

A 3D object created by an ACIS based geometry kernel provided by the `Spatial Corp.`_
Create :class:`Surface` objects in layouts and blocks by factory function
:meth:`~Layout.add_surface`.

DXF Attributes for Surface
--------------------------

:ref:`Common DXF attributes for DXF R13 or later`

.. attribute:: Surface.dxf.u_count

Number of U isolines

.. attribute:: Surface.dxf.v_count

Number of V isolines

Extended DXF data for ExtrudedSurface, LoftedSurface, RevolvedSurface, SweptSurfacenot supported (yet).

Surface Methods
---------------

.. method:: Surface.get_acis_data()

Get the ACIS source code as a list of strings.

.. method:: Surface.set_acis_data(test_lines)

Set the ACIS source code as a list of strings **without** line endings.

.. method:: Surface.edit_data()

Context manager for ACIS text lines, returns :class:`ModelerGeometryData`.

.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

