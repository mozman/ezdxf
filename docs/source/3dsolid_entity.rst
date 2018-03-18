
3DSolid
=======

.. class:: 3DSolid(Body)

Introduced in DXF version R13 (AC1012), dxftype is 3DSOLID.

A 3D object created by an ACIS based geometry kernel provided by the `Spatial Corp.`_
Create :class:`3DSolid` objects in layouts and blocks by factory function
:meth:`~Layout.add_3dsolid`.

.. method:: 3DSolid.get_acis_data()

Get the ACIS source code as a list of strings.

.. method:: 3DSolid.set_acis_data(test_lines)

Set the ACIS source code as a list of strings **without** line endings.

.. method:: 3DSolid.edit_data()

Context manager for  ACIS text lines, returns :class:`ModelerGeometryData`.

DXF Attributes for 3DSolid
--------------------------

.. attribute:: 3DSolid.dxf.history

Handle to history object, see: :ref:`low_level_access_to_dxf_entities`


.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

