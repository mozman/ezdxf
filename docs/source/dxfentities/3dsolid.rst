
3DSolid
=======

.. class:: 3DSolid(Body)

    Introduced in DXF R13 (AC1012), dxftype is 3DSOLID.

    A 3D object created by an ACIS based geometry kernel provided by the `Spatial Corp.`_
    Create :class:`3DSolid` objects in layouts and blocks by factory function :meth:`~ezdxf.modern.layouts.Layout.add_3dsolid`.

    :ref:`Common graphical DXF attributes`

    .. attribute:: dxf.history

        Handle to history object.

    .. method:: get_acis_data()

        Get the ACIS source code as a list of strings.

    .. method:: set_acis_data(test_lines)

        Set the ACIS source code as a list of strings **without** line endings.

    .. method:: edit_data()

        Context manager for  ACIS text lines, returns :class:`ModelerGeometryData`.

.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

