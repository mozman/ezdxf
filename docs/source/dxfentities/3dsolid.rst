Solid3d
=======

.. module:: ezdxf.entities
    :noindex:

3DSOLID entity (`DXF Reference`_) created by an ACIS geometry kernel provided by
the `Spatial Corp.`_


.. seealso::

    `Ezdxf` has only very limited support for ACIS based entities, for more
    information see the FAQ: :ref:`faq003`

======================== ==========================================
Subclass of              :class:`ezdxf.entities.Body`
DXF type                 ``'3DSOLID'``
Factory function         :meth:`ezdxf.layouts.BaseLayout.add_3dsolid`
Inherited DXF attributes :ref:`Common graphical DXF attributes`
Required DXF version     DXF R2000 (``'AC1015'``)
======================== ==========================================

.. warning::

    Do not instantiate entity classes by yourself - always use the provided factory functions!

.. class:: Solid3d

    Same attributes and methods as parent class :class:`Body`.

    .. attribute:: dxf.history_handle

        Handle to history object.


.. _Spatial Corp.: http://www.spatial.com/products/3d-acis-modeling

.. _DXF Reference: http://help.autodesk.com/view/OARX/2018/ENU/?guid=GUID-19AB1C40-0BE0-4F32-BCAB-04B37044A0D3