Region
======

.. class:: Region(Body)

Introduced in DXF version R13 (AC1012), dxftype is REGION.

An object created by an ACIS based geometry kernel provided by the `Spatial Corp.`_
Create :class:`Region` objects in layouts and blocks by factory function
:meth:`~Layout.add_region`.

.. method:: Region.get_acis_data()

Get the ACIS source code as a list of strings.

.. method:: Region.set_acis_data(test_lines)

Set the ACIS source code as a list of strings **without** line endings.

.. method:: Region.edit_data()

Context manager for ACIS text lines, returns :class:`ModelerGeometryData`.

.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling
