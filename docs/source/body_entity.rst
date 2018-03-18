Body
====

.. class:: Body(GraphicEntity)

Introduced in DXF version R13 (AC1012), dxftype is BODY.

A 3D object created by an ACIS based geometry kernel provided by the `Spatial Corp.`_
Create :class:`Body` objects in layouts and blocks by factory function :meth:`~Layout.add_body`.
*ezdxf* will never interpret ACIS source code, don't ask me for this feature.

.. method:: Body.get_acis_data()

Get the ACIS source code as a list of strings.

.. method:: Body.set_acis_data(test_lines)

Set the ACIS source code as a list of strings **without** line endings.

.. method:: Body.edit_data()

Context manager for  ACIS text lines, returns :class:`ModelerGeometryData`::

    with body_entity.edit_data as data:
        # data.text_lines is a standard Python list
        # remove, append and modify ACIS source code
        data.text_lines = ['line 1', 'line 2', 'line 3']  # replaces the whole ACIS content (with invalid data)



ModelerGeometryData
-------------------

.. class:: ModelerGeometryData:

.. attribute:: ModelerGeometryData.text_lines

ACIS date as list of strings. (read/write)

.. method:: ModelerGeometryData.__str__()

Return concatenated :attr:`~ModelerGeometryData.text_lines` as one string, lines are separated by ``\n``.

.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling